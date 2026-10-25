"""A scripted model (PRD L-05): replays fixed replies so the loop is tested without the API."""

from anthropic.types import Message, TextBlock, ToolUseBlock, Usage


def tool(name, **args):
    return ("tool", name, args)


def text(t):
    return ("text", t)


class ScriptedClient:
    def __init__(self, *turns):
        self.turns = list(turns)
        self.requests = []
        self.messages = self

    def create(self, **params):
        # The agent keeps appending to one list; record what this request saw.
        self.requests.append({**params, "messages": list(params["messages"])})
        blocks = []
        for i, item in enumerate(self.turns.pop(0)):
            if item[0] == "tool":
                blocks.append(ToolUseBlock(type="tool_use", id=f"t{len(self.requests)}-{i}", name=item[1], input=item[2]))
            else:
                blocks.append(TextBlock(type="text", text=item[1]))
        stop = "tool_use" if any(b.type == "tool_use" for b in blocks) else "end_turn"
        return Message(id=f"m{len(self.requests)}", type="message", role="assistant", model=params["model"],
                       content=blocks, stop_reason=stop, stop_sequence=None,
                       usage=Usage(input_tokens=10, output_tokens=5))
