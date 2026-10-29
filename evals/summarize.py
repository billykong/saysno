"""Generate a results directory's summary.md from its runs.jsonl (PRD E-09).

    uv run python -m evals.summarize results/m2

CI regenerates every summary and fails if the committed one differs, so no number
in a summary is typed in by hand.
"""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from .tasks import ROOT, retired


def load_runs(results):
    return [json.loads(line) for line in (Path(results) / "runs.jsonl").read_text().splitlines() if line]


def mean(values):
    return sum(values) / len(values) if values else 0


def features(run):
    """Runs from before L-07 have no feature list; label them as they were."""
    if "features" not in run:
        return ""
    return f"; features: {', '.join(run['features'])}" if run["features"] else "; bare loop"


def prompt(run):
    """Input tokens, cached or not."""
    return run["input_tokens"] + run.get("cache_read_tokens", 0) + run.get("cache_write_tokens", 0)


def cached(rs):
    read, write = sum(r.get("cache_read_tokens", 0) for r in rs), sum(r.get("cache_write_tokens", 0) for r in rs)
    return f", plus {read:,} read from and {write:,} written to the prompt cache" if read or write else ""


def render(runs):
    gone = retired()
    by_model = defaultdict(list)
    for r in runs:
        if r["task"] not in gone:
            by_model[(r["model_id"], r["thinking"], r["effort"], features(r))].append(r)

    out = ["# Results", "", "Generated from `runs.jsonl` by `python -m evals.summarize`. Do not edit by hand.", ""]
    for (model_id, thinking, effort, feats), rs in sorted(by_model.items()):
        passed = sum(r["passed"] for r in rs)
        out += [f"## {model_id} (thinking {thinking}, effort {effort}{feats})", "",
                f"**{passed}/{len(rs)} runs passed** ({100 * passed / len(rs):.0f}%) "
                f"across {len({r['task'] for r in rs})} tasks. "
                f"Total cost ${sum(r['cost_usd'] for r in rs):.4f}; "
                f"{sum(r['input_tokens'] for r in rs):,} input and {sum(r['output_tokens'] for r in rs):,} output tokens"
                + cached(rs) + ".", ""]

        if "capped_outputs" in rs[0]:
            out += [f"Largest prompt {max(r['max_prompt_tokens'] for r in rs):,} tokens; "
                    f"{sum(len(r['denials']) for r in rs)} of {sum(r['bash_calls'] for r in rs)} `bash` calls denied; "
                    f"{sum(r['capped_outputs'] for r in rs)} tool outputs capped; "
                    f"tests ran in {sum(r['tests_ran'] for r in rs)} of {len(rs)} runs.", ""]
        added = sum(bool(r.get("tests_added")) for r in rs)
        if added:
            out += [f"{added} of {len(rs)} runs added tests (allowed; existing tests must be kept).", ""]
        out += ["| Difficulty | Passed |", "| --- | --- |"]
        for level in ("easy", "medium", "hard"):
            group = [r for r in rs if r["difficulty"] == level]
            if group:
                out.append(f"| {level} | {sum(r['passed'] for r in group)}/{len(group)} |")
        out.append("")

        out += ["| Task | Difficulty | Provokes | Passed | Calls (mean) | Prompt tokens (mean) | Cost (mean) | Stops | Why runs failed |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        by_task = defaultdict(list)
        for r in rs:
            by_task[r["task"]].append(r)
        for task, trs in sorted(by_task.items()):
            stops = ", ".join(f"{s} ×{n}" for s, n in sorted(Counter(r["stop"] for r in trs).items()))
            reasons = Counter(reason.split(":")[0] for r in trs for reason in r["reasons"])
            why = ", ".join(f"{s} ×{n}" for s, n in sorted(reasons.items())) or "-"
            out.append(f"| {task} | {trs[0]['difficulty']} | {', '.join(trs[0]['provokes']) or '-'} | "
                       f"{sum(r['passed'] for r in trs)}/{len(trs)} | {mean([r['calls'] for r in trs]):.1f} | "
                       f"{mean([prompt(r) for r in trs]):,.0f} | ${mean([r['cost_usd'] for r in trs]):.4f} | "
                       f"{stops} | {why} |")
        out.append("")

        denied = Counter(d for r in rs for d in r["denials"])
        if denied:
            out += ["Commands denied (batch mode turns every ask into a deny):", ""]
            out += [f"- `{cmd}` ×{n}" for cmd, n in sorted(denied.items(), key=lambda kv: (-kv[1], kv[0]))]
            out.append("")

    old = [r for r in runs if r["task"] in gone]
    if old:
        out += ["## Retired tasks (not scored)", "", "See `evals/retired.toml` for why.", "",
                "| Task | Model | Passed | Replaced by |", "| --- | --- | --- | --- |"]
        groups = defaultdict(list)
        for r in old:
            groups[(r["task"], r["model_id"])].append(r)
        for (task, model_id), rs in sorted(groups.items()):
            out.append(f"| {task} | {model_id} | {sum(r['passed'] for r in rs)}/{len(rs)} | {gone[task]['replaced_by']} |")
        out.append("")
    return "\n".join(out)


def main():
    for results in sys.argv[1:]:
        path = ROOT / results / "summary.md"
        path.write_text(render(load_runs(ROOT / results)))
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
