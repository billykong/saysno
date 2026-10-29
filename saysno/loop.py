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
# C-02: steer toward small reads (context level 3).
STEER = """ Find code with grep, then read only the lines you need with read_file offset and \
limit. Don't read whole data files or large files at once."""
OUTPUT_CAP = 10_000  # characters (C-01)

# Features added after M1 (PRD L-07). Each can be switched off; with none, this is the M1 loop.
FEATURES = {
    "output-cap": "C-01: tool output over OUTPUT_CAP is cut, with a notice saying how to see the rest",
    "denial-help": "T-06: a denial says why, and what runs without asking",
    "trim-pipes": "F-02: a trailing `2>&1`, `| head` or `| tail` doesn't need asking",
    "steer": "C-02: the system prompt steers toward grep and ranged reads",
    "cache": "C-03: prompt caching on the growing conversation",
}

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
    def __init__(self, client, root, model="haiku", ask=policy.ask_user, transcript=None, show=print,
                 features=FEATURES):
        self.client, self.tools, self.params = client, Tools(root), dict(MODELS[model])
        self.ask, self.show, self.messages, self.features = ask, show, [], set(features)
        # The stable prefix (tools, system) never changes within a run, so every request
        # can read the previous one's cache. DeepSeek caches on its own (L-08).
        self.system = SYSTEM + (STEER if "steer" in self.features else "")
        if "cache" in self.features and model not in ENDPOINTS:
            self.params["cache_control"] = {"type": "ephemeral"}
        self.transcript = open(transcript, "a") if transcript else None
        self.log("start", model=self.params["model"], root=str(self.tools.root), features=sorted(self.features))

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
            reply = self.client.messages.create(max_tokens=16000, system=self.system, tools=TOOLS,
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
        decision, why = policy.check(block.name, block.input, trim="trim-pipes" in self.features)
        if decision == "ask":
            decision = "allow" if self.ask(block.name, block.input) else "deny"
        if decision == "deny":
            output, is_error = self.denial(why), True
        else:
            try:
                output, is_error = self.tools.run(block.name, block.input), False
            except ToolError as e:
                output, is_error = f"error: {e}", True
        full = len(output)
        if "output-cap" in self.features and full > OUTPUT_CAP:
            output = cap(output)
        self.log("tool", name=block.name, input=block.input, decision=decision, output=output,
                 is_error=is_error, chars=full)
        return {"type": "tool_result", "tool_use_id": block.id, "content": output, "is_error": is_error}

    def denial(self, why):
        if "denial-help" not in self.features:
            return "denied: the user did not allow this command"
        allowed = "; a trailing `2>&1`, `| head -N` or `| tail -N` is fine" if "trim-pipes" in self.features else ""
        capped = " Tool output is capped, so it doesn't need trimming." if "output-cap" in self.features else ""
        return (f"denied: this needs the user's approval because {why}, and it was not approved. "
                f"Commands that start with one of {', '.join(f'`{p}`' for p in policy.ALLOW)} and contain no ; & | ` $ < > "
                f"or newline run without approval{allowed}. Run one command per call.{capped}")


def cap(text, limit=OUTPUT_CAP):
    """Keep the start and the end, where errors and test summaries are."""
    head, tail = text[:limit * 3 // 4], text[-(limit // 4):]
    cut = len(text) - len(head) - len(tail)
    return (f"{head}\n[... {cut:,} characters cut: tool output is capped at {limit:,}. To see more, read a "
            f"range with read_file offset and limit, narrow the grep pattern or path, or run a command that "
            f"prints less ...]\n{tail}")
