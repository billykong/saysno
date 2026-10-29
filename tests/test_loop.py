import json
import shutil
import subprocess
from pathlib import Path

import pytest

from saysno.loop import FEATURES, MODELS, OUTPUT_CAP, SYSTEM, Agent, cap, make_client
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
    assert MODELS["deepseek-flash"]["thinking"] == {"type": "disabled"}


def test_other_providers_get_their_own_endpoint_and_key(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    client = make_client("deepseek-flash")
    assert str(client.base_url).startswith("https://api.deepseek.com/anthropic") and client.api_key == "test-key"


def bare_agent(tmp_path, client, **kw):
    project = tmp_path / "project"
    shutil.copytree(EXAMPLE, project)
    return Agent(client, project, transcript=tmp_path / "t.jsonl", show=lambda s: None, **kw), project


def test_long_tool_output_is_capped_with_a_notice(tmp_path):
    # C-01 and F-08: grep "." over a big file must not flood the context.
    client = ScriptedClient([tool("grep", pattern=".", path="big.txt")], [text("ok")])
    agent, project = bare_agent(tmp_path, client)
    (project / "big.txt").write_text("".join(f"line {i}\n" for i in range(20_000)))
    agent.send("look")
    result = client.requests[1]["messages"][-1]["content"][0]["content"]
    assert len(result) < OUTPUT_CAP + 500
    assert result.startswith("big.txt:1:line 0") and result.endswith("big.txt:20000:line 19999")
    assert "characters cut: tool output is capped at 10,000" in result and "read_file offset and limit" in result
    logged = [json.loads(l) for l in (tmp_path / "t.jsonl").read_text().splitlines()][-2]
    assert logged["chars"] > 300_000 and logged["output"] == result


def test_short_output_and_the_bare_loop_are_not_capped(tmp_path):
    client = ScriptedClient([tool("grep", pattern=".", path="big.txt")], [text("ok")])
    agent, project = bare_agent(tmp_path, client, features=set(FEATURES) - {"output-cap"})
    (project / "big.txt").write_text("x\n" * 20_000)
    agent.send("look")
    assert len(client.requests[1]["messages"][-1]["content"][0]["content"]) > 100_000
    assert len(cap("y" * 50_000)) < OUTPUT_CAP + 500


def test_denial_says_why_and_what_would_run(tmp_path):
    # T-06 and F-02.
    client = ScriptedClient([tool("bash", command="python -m pytest -q; echo done")], [text("ok")])
    agent, _ = bare_agent(tmp_path, client, ask=lambda name, args: False)
    agent.send("test")
    result = client.requests[1]["messages"][-1]["content"][0]
    assert result["is_error"] and result["content"].startswith("denied:")
    assert "';'" in result["content"] and "`python -m pytest`" in result["content"]
    assert "Run one command per call" in result["content"] and "capped" in result["content"]


def test_trim_pipes_lets_the_tests_run(tmp_path):
    client = ScriptedClient([tool("bash", command="python -m pytest -q 2>&1 | tail -3")], [text("ok")])
    agent, _ = bare_agent(tmp_path, client, ask=lambda name, args: pytest.fail("should not ask"))
    agent.send("test")
    result = client.requests[1]["messages"][-1]["content"][0]
    assert not result["is_error"] and "exit code" in result["content"]


def test_stable_prefix_and_cache_control(tmp_path):
    # C-03: tools and system are identical on every request; the conversation only grows.
    client = ScriptedClient([tool("read_file", path="stats.py")], [tool("grep", pattern="def")], [text("ok")])
    agent, _ = bare_agent(tmp_path, client)
    agent.send("look")
    first, *rest = client.requests
    assert all(r["system"] == first["system"] and r["tools"] == first["tools"] for r in rest)
    assert all(r["messages"][:len(first["messages"])] == first["messages"] for r in rest)
    assert all(r["cache_control"] == {"type": "ephemeral"} for r in client.requests)
    assert "grep" in first["system"] and "offset" in first["system"]  # C-02


def test_bare_loop_is_the_m1_loop(tmp_path):
    # L-07: with every feature off, the requests and denials are what M1 sent.
    client = ScriptedClient([tool("bash", command="pytest 2>&1 | tail")], [text("ok")])
    agent, _ = bare_agent(tmp_path, client, features=set(), ask=lambda name, args: False)
    agent.send("test")
    assert all("cache_control" not in r for r in client.requests)
    assert client.requests[0]["system"] == SYSTEM
    assert client.requests[1]["messages"][-1]["content"][0]["content"] == "denied: the user did not allow this command"


def test_other_providers_get_no_cache_control(tmp_path):
    client = ScriptedClient([text("hi")])
    agent, project = make_agent(tmp_path, client)
    agent = Agent(client, project, "deepseek-flash", show=lambda s: None)
    agent.send("hello")
    assert "cache_control" not in client.requests[0]
