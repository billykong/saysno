import json
import shutil
import subprocess
from pathlib import Path

from saysno.loop import MODELS, Agent
from scripted import ScriptedClient, text, tool

EXAMPLE = Path(__file__).parent.parent / "examples" / "first-task"


def make_agent(tmp_path, client, ask=lambda name, args: False):
    project = tmp_path / "project"
    shutil.copytree(EXAMPLE, project)
    return Agent(client, project, ask=ask, transcript=tmp_path / "t.jsonl", show=lambda s: None), project


def test_scripted_fix_of_the_example_task(tmp_path):
    client = ScriptedClient(
        [text("Looking."), tool("grep", pattern="def mean")],
        [tool("read_file", path="stats.py")],
        [tool("edit_file", path="stats.py", old="(len(values) - 1)", new="len(values)")],
        [tool("bash", command="python -m pytest -q")],
        [text("Fixed the off-by-one in mean().")],
    )
    agent, project = make_agent(tmp_path, client)
    reply = agent.send((project / "TASK.md").read_text())

    assert reply.stop_reason == "end_turn"
    assert subprocess.run(["python", "-m", "pytest", "-q"], cwd=project).returncode == 0
    # Each tool result goes back in the next request, matched to its call.
    last = client.requests[-1]["messages"][-1]["content"][0]
    assert last["tool_use_id"] == "t4-0" and "3 passed" in last["content"] and not last["is_error"]
    events = [json.loads(l)["event"] for l in (tmp_path / "t.jsonl").read_text().splitlines()]
    assert events == ["start", "user"] + ["reply", "tool"] * 4 + ["reply"]


def test_denied_command_is_reported_to_the_model_not_run(tmp_path):
    asked = []
    client = ScriptedClient([tool("bash", command="rm stats.py")], [text("ok")])
    agent, project = make_agent(tmp_path, client, ask=lambda name, args: asked.append(args) or False)
    agent.send("delete it")

    assert asked == [{"command": "rm stats.py"}]
    assert (project / "stats.py").exists()
    result = client.requests[1]["messages"][-1]["content"][0]
    assert result["is_error"] and result["content"].startswith("denied")


def test_tool_errors_go_back_to_the_model(tmp_path):
    client = ScriptedClient([tool("edit_file", path="stats.py", old="nope", new="x")], [text("ok")])
    agent, _ = make_agent(tmp_path, client)
    agent.send("edit")
    result = client.requests[1]["messages"][-1]["content"][0]
    assert result["is_error"] and "found 0 times" in result["content"]


def test_several_calls_in_one_reply_return_in_one_message(tmp_path):
    client = ScriptedClient([tool("read_file", path="stats.py"), tool("read_file", path="test_stats.py")], [text("ok")])
    agent, _ = make_agent(tmp_path, client)
    agent.send("read both")
    results = client.requests[1]["messages"][-1]["content"]
    assert [r["tool_use_id"] for r in results] == ["t1-0", "t1-1"]


def test_model_settings_per_l04(tmp_path):
    client = ScriptedClient([text("hi")])
    agent, _ = make_agent(tmp_path, client)
    agent.send("hello")
    assert client.requests[0]["model"] == "claude-haiku-5-5"
    assert client.requests[0]["thinking"] == {"type": "disabled"}
    assert MODELS["opus"]["thinking"] == {"type": "adaptive"}
