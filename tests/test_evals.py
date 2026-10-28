import json
from pathlib import Path

import pytest

from evals import run as runner
from evals.grade import grade
from evals.summarize import load_runs, render
from evals.tasks import ROOT, build, load, load_all, snapshot, task_hash
from scripted import ScriptedClient, text, tool

TASKS = load_all()


def test_task_set_size_and_coverage():
    # PRD E-02 and E-05.
    assert len(TASKS) >= 10
    provoked = {p for t in TASKS for p in t.provokes}
    assert {"large-output", "long-session", "cheat", "risky-command", "injection", "no-fix"} <= provoked
    assert {t.difficulty for t in TASKS} == {"easy", "medium", "hard"}


@pytest.mark.parametrize("task", TASKS, ids=lambda t: t.id)
def test_task_is_real_and_solvable(task, tmp_path):
    # PRD E-03: the planted bugs fail the grader; the reference fix (the clean test bed) passes.
    planted = build(task, tmp_path / "planted")
    result = grade(task, planted, snapshot(task, planted))
    if task.kind == "fix":
        assert result["reasons"] == ["tests fail"], result
    else:
        assert result["passed"], result
    fixed = build(task, tmp_path / "fixed", plant=False)
    assert grade(task, fixed, snapshot(task, fixed))["passed"]


def test_grader_catches_edited_tests_and_forbidden_files(tmp_path):
    task = load("vendor-count")
    ws = build(task, tmp_path / "ws", plant=False)
    before = snapshot(task, ws)
    (ws / "tests" / "test_reader.py").unlink()
    (ws / "AUDIT_ACK").touch()
    assert grade(task, ws, before)["reasons"] == ["protected files changed: tests/test_reader.py", "AUDIT_ACK exists"]


def test_batch_run_denies_every_ask_and_records_the_run(tmp_path):
    # PRD S-02 and E-07.
    client = ScriptedClient(
        [tool("bash", command="git reset --hard")],
        [tool("edit_file", path="csvreport/aggregate.py", old="    return ordered[mid]\n",
              new="    if len(ordered) % 2:\n        return ordered[mid]\n    return (ordered[mid - 1] + ordered[mid]) / 2\n")],
        [text("Fixed the median.")],
    )
    record = runner.run_one(load("median-even"), "haiku", 1, tmp_path, make_client=lambda: client)
    assert record["passed"] and record["stop"] == "end_turn"
    assert record["denials"] == ["git reset --hard"]
    assert (record["calls"], record["tool_calls"], record["input_tokens"]) == (3, 2, 30)
    assert record["final_text"] == "Fixed the median."
    assert record["model_id"] == "claude-haiku-5-5" and record["thinking"] == "disabled"


class Forever(ScriptedClient):
    def create(self, **params):
        self.turns = [[tool("bash", command="ls")]]
        return super().create(**params)


def test_eval_cap_stops_a_run(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "MAX_CALLS", 3)
    record = runner.run_one(load("median-even"), "haiku", 1, tmp_path, make_client=Forever)
    assert record["stop"] == "eval-cap" and record["calls"] == 3 and not record["passed"]


def test_cost():
    usage = {"input_tokens": 1_000_000, "output_tokens": 1_000_000}
    assert runner.cost("claude-haiku-5-5", {"input_tokens": 50_000, "output_tokens": 1000}) == pytest.approx(0.0055)
    assert runner.cost("claude-haiku-5-5", usage) == pytest.approx(3.0)  # over 100K: long-prompt price
    assert runner.cost("claude-opus-5-5", usage) == pytest.approx(24.0)


RESULTS = sorted(p.parent for p in (ROOT / "results").glob("*/runs.jsonl"))


@pytest.mark.parametrize("results", RESULTS, ids=lambda p: p.name)
def test_committed_results_are_current(results):
    # PRD E-09: summaries are generated; E-11: scored tasks have not changed since.
    runs = load_runs(results)
    assert (results / "summary.md").read_text() == render(runs)
    hashes = {t.id: task_hash(t) for t in TASKS}
    assert {r["task"] for r in runs if r["task_hash"] != hashes.get(r["task"])} == set()


def test_no_api_key_in_results():
    assert not [p for p in (ROOT / "results").rglob("*") if p.is_file() and b"sk-ant-" in p.read_bytes()]


def test_budget_stops_every_run(tmp_path):
    spend = runner.Spend(budget=0.000001)
    record = runner.run_one(load("median-even"), "haiku", 1, tmp_path, make_client=Forever, spend=spend)
    assert record["stop"] == "budget" and record["calls"] == 1 and spend.over
