"""Run tasks against the agent and record one line per run (PRD E-07, E-08).

    uv run python -m evals.run --model haiku --runs 3 --out results/m3 [--task ID ...] [--off FEATURE ...] [--bare]

Batch mode: nobody is there to answer, so every "ask" is a "deny" (PRD S-02).
Each run is capped at MAX_CALLS model calls and MAX_INPUT_TOKENS input tokens. The cap
protects the budget; it is the experiment's guard, not an agent feature, and a run
that hits it is recorded as stop "eval-cap".
"""

import argparse
import json
import os
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import anthropic

from saysno.loop import FEATURES, MODELS, Agent
from saysno.loop import make_client as _client

from .grade import grade, snapshot
from .tasks import ROOT, build, load, load_all, task_hash

MAX_CALLS = 60
MAX_INPUT_TOKENS = 3_000_000

# USD per million tokens (Anthropic API list prices, October 2026). Haiku 5.5 charges more
# for a request whose prompt is over 100K tokens. Cache writes (5-minute) cost 1.25x input,
# reads 0.1x unless the model says otherwise.
PRICES = {
    "claude-haiku-5-5": {"input": 0.10, "output": 0.50, "long_input": 0.50, "long_output": 2.50, "long_from": 100_000},
    "claude-opus-5-5": {"input": 4.00, "output": 20.00},
    # DeepSeek peak prices (off-peak is half), October 2026. It caches prompts automatically.
    "deepseek-flash": {"input": 0.30, "output": 1.20, "cache_read": 0.006},
}


class EvalCap(Exception):
    pass


class Spend:
    """Total spend across all runs; once over the budget, every run stops (stop "budget")."""

    def __init__(self, budget=None):
        self.budget, self.total, self.lock = budget, 0.0, threading.Lock()

    def add(self, amount):
        with self.lock:
            self.total += amount

    @property
    def over(self):
        return self.budget is not None and self.total >= self.budget


class OverBudget(Exception):
    pass


class CappedClient:
    """Wraps the API client and stops a run that goes over the cap."""

    def __init__(self, client, spend=None):
        self.client, self.messages, self.spend = client, self, spend or Spend()
        self.calls = self.input_tokens = 0

    def create(self, **params):
        if self.spend.over:
            raise OverBudget(f"${self.spend.total:.2f} spent")
        if self.calls >= MAX_CALLS or self.input_tokens >= MAX_INPUT_TOKENS:
            raise EvalCap(f"{self.calls} calls, {self.input_tokens} input tokens")
        reply = self.client.messages.create(**params)
        self.calls += 1
        self.input_tokens += reply.usage.input_tokens
        self.spend.add(cost(params["model"], reply.usage.to_dict()))
        return reply


def cost(model_id, usage):
    p = PRICES[model_id]
    read, write = usage.get("cache_read_input_tokens") or 0, usage.get("cache_creation_input_tokens") or 0
    long = "long_from" in p and usage["input_tokens"] + read + write > p["long_from"]
    i, o = (p["long_input"], p["long_output"]) if long else (p["input"], p["output"])
    return (usage["input_tokens"] * i + read * p.get("cache_read", i * 0.1) + write * i * 1.25
            + usage["output_tokens"] * o) / 1e6


def prompt_tokens(usage):
    """The whole prompt, cached or not."""
    return usage["input_tokens"] + (usage.get("cache_read_input_tokens") or 0) + (usage.get("cache_creation_input_tokens") or 0)


def measure(model_id, transcript):
    events = [json.loads(line) for line in transcript.read_text().splitlines()]
    replies = [e for e in events if e["event"] == "reply"]
    tools = [e for e in events if e["event"] == "tool"]
    usage = [r["usage"] for r in replies]
    final = replies[-1]["content"] if replies else []
    return {
        "calls": len(replies),
        "tool_calls": len(tools),
        "denials": [t["input"].get("command", t["name"]) for t in tools if t["decision"] == "deny"],
        "tool_errors": sum(t["is_error"] and t["decision"] != "deny" for t in tools),
        "input_tokens": sum(u["input_tokens"] for u in usage),
        "output_tokens": sum(u["output_tokens"] for u in usage),
        "cache_read_tokens": sum(u.get("cache_read_input_tokens") or 0 for u in usage),
        "cache_write_tokens": sum(u.get("cache_creation_input_tokens") or 0 for u in usage),
        "max_prompt_tokens": max((prompt_tokens(u) for u in usage), default=0),
        "bash_calls": sum(t["name"] == "bash" for t in tools),
        "tests_ran": any(t["name"] == "bash" and t["decision"] == "allow" and "pytest" in t["input"].get("command", "")
                         for t in tools),
        "capped_outputs": sum(t.get("chars", 0) > len(t["output"]) for t in tools),
        "cost_usd": round(sum(cost(model_id, u) for u in usage), 6),
        "final_text": " ".join(b["text"] for b in final if b["type"] == "text")[:1000],
    }


def redact(path):
    """Keep any API key the agent may have printed out of committed transcripts."""
    text = path.read_text()
    for name in ("ANTHROPIC_API_KEY", "DEEPSEEK_API_KEY"):
        key = os.environ.get(name)
        if key and key in text:
            text = text.replace(key, "[REDACTED]")
    path.write_text(text)


def run_one(task, model, run, out, make_client=None, spend=None, features=FEATURES):
    transcript = out / "transcripts" / model / f"{task.id}-{run}.jsonl"
    transcript.parent.mkdir(parents=True, exist_ok=True)
    transcript.unlink(missing_ok=True)
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="saysno-") as tmp:
        workspace = build(task, Path(tmp) / task.id)
        before = snapshot(task, workspace)
        client = CappedClient(make_client() if make_client else _client(model, max_retries=6), spend)
        agent = Agent(client, workspace, model, ask=lambda name, args: False,
                      transcript=transcript, show=lambda text: None, features=features)
        try:
            stop = agent.send(task.ticket).stop_reason
        except EvalCap:
            stop = "eval-cap"
        except OverBudget:
            stop = "budget"
        except anthropic.APIError as e:
            stop = f"api-error: {type(e).__name__}"
        agent.transcript.close()
        result = grade(task, workspace, before)
    redact(transcript)
    params = MODELS[model]
    return {
        "task": task.id, "task_hash": task_hash(task), "difficulty": task.difficulty, "kind": task.kind,
        "provokes": task.provokes, "model": model, "model_id": params["model"],
        "thinking": params["thinking"]["type"], "effort": params["output_config"]["effort"],
        "features": sorted(features), "run": run, "stop": stop, "seconds": round(time.monotonic() - started, 1),
        **result, **measure(params["model"], transcript),
        "transcript": os.path.relpath(transcript, ROOT),
    }


def main():
    parser = argparse.ArgumentParser(prog="evals.run")
    parser.add_argument("--model", choices=MODELS, default="haiku")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--out", required=True, help="results directory, e.g. results/m2")
    parser.add_argument("--task", action="append", help="task id; default all")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--budget", type=float, help="stop every run once this many USD are spent")
    parser.add_argument("--off", action="append", default=[], choices=FEATURES, help="switch a feature off (L-07)")
    parser.add_argument("--bare", action="store_true", help="every feature off: the M1 loop")
    args = parser.parse_args()
    features = set() if args.bare else set(FEATURES) - set(args.off)
    spend = Spend(args.budget)

    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)
    tasks = [load(t) for t in args.task] if args.task else load_all()
    jobs = [(t, r) for r in range(1, args.runs + 1) for t in tasks]
    with ThreadPoolExecutor(args.workers) as pool, open(out / "runs.jsonl", "a") as log:
        def job(task_run):
            if spend.over:
                return None  # not started: the budget was used up
            return run_one(task_run[0], args.model, task_run[1], out, spend=spend, features=features)

        for record in pool.map(job, jobs):
            if record is None or record["stop"] == "budget":
                continue  # a run cut short by the budget is not a result
            log.write(json.dumps(record) + "\n")
            log.flush()
            print(f"{record['task']:22} run {record['run']}  {'PASS' if record['passed'] else 'fail'}  "
                  f"{record['calls']:3} calls  ${record['cost_usd']:.4f}  {record['stop']}  {'; '.join(record['reasons'])}")
    print(f"spent ${spend.total:.4f}" + (f" of ${spend.budget:.2f}: BUDGET REACHED, runs stopped" if spend.over else ""))


if __name__ == "__main__":
    main()
