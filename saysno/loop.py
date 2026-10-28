"""The agent loop: build context, call the model, check and run tools, append, repeat."""

import json
import os
from datetime import datetime, timezone

import anthropic

from . import policy
from .tools import TOOLS, ToolError, Tools

SYSTEM = """You are a coding agent working in a project directory. Use the tools to \
read, search, edit and test the code. Make the smallest change that fixes the problem, \
run the tests, and say what you changed."""

# How each model is run (PRD L-04): Haiku without thinking, Opus with adaptive thinking.
MODELS = {
    "haiku": {"model": "claude-haiku-5-5", "thinking": {"type": "disabled"}, "output_config": {"effort": "high"}},
    "opus": {"model": "claude-opus-5-5", "thinking": {"type": "adaptive"}, "output_config": {"effort": "high"}},
    # A side comparison from another provider, run like Haiku (PRD L-08).
    "deepseek-flash": {"model": "deepseek-flash", "thinking": {"type": "disabled"}, "output_config": {"effort": "high"}},
}
# Models served through another provider's Anthropic-compatible API: base URL and key variable.
ENDPOINTS = {"deepseek-flash": ("https://api.deepseek.com/anthropic", "DEEPSEEK_API_KEY")}


def make_client(model, max_retries=2):
    if model in ENDPOINTS:
        url, key = ENDPOINTS[model]
        return anthropic.Anthropic(base_url=url, api_key=os.environ[key], max_retries=max_retries)
    return anthropic.Anthropic(max_retries=max_retries)


class Agent:
    def __init__(self, client, root, model="haiku", ask=policy.ask_user, transcript=None, show=print):
        self.client, self.tools, self.params = client, Tools(root), MODELS[model]
        self.ask, self.show, self.messages = ask, show, []
        self.transcript = open(transcript, "a") if transcript else None
        self.log("start", model=self.params["model"], root=str(self.tools.root))

    def log(self, event, **data):
        if self.transcript:
            data = {"time": datetime.now(timezone.utc).isoformat(), "event": event, **data}
            self.transcript.write(json.dumps(data) + "\n")
            self.transcript.flush()

    def send(self, text):
        """Run one user request to completion; return the final reply."""
        self.messages.append({"role": "user", "content": text})
        self.log("user", text=text)
        while True:
            reply = self.client.messages.create(max_tokens=16000, system=SYSTEM, tools=TOOLS,
                                                messages=self.messages, **self.params)
            self.log("reply", **reply.to_dict())
            self.messages.append({"role": "assistant", "content": reply.content})
            for block in reply.content:
                if block.type == "text":
                    self.show(block.text)
            if reply.stop_reason != "tool_use":
                return reply
            results = [self.call(b) for b in reply.content if b.type == "tool_use"]
            self.messages.append({"role": "user", "content": results})

    def call(self, block):
        """Stage 3: the harness decides whether the requested tool runs."""
        self.show(f"→ {block.name} {json.dumps(block.input)[:200]}")
        decision = policy.decide(block.name, block.input)
        if decision == "ask":
            decision = "allow" if self.ask(block.name, block.input) else "deny"
        if decision == "deny":
            output, is_error = "denied: the user did not allow this command", True
        else:
            try:
                output, is_error = self.tools.run(block.name, block.input), False
            except ToolError as e:
                output, is_error = f"error: {e}", True
        self.log("tool", name=block.name, input=block.input, decision=decision, output=output, is_error=is_error)
        return {"type": "tool_result", "tool_use_id": block.id, "content": output, "is_error": is_error}
