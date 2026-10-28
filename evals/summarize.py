"""Generate a results directory's summary.md from its runs.jsonl (PRD E-09).

    uv run python -m evals.summarize results/m2

CI regenerates every summary and fails if the committed one differs, so no number
in a summary is typed in by hand.
"""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from .tasks import ROOT


def load_runs(results):
    return [json.loads(line) for line in (Path(results) / "runs.jsonl").read_text().splitlines() if line]


def mean(values):
    return sum(values) / len(values) if values else 0


def render(runs):
    by_model = defaultdict(list)
    for r in runs:
        by_model[(r["model_id"], r["thinking"], r["effort"])].append(r)

    out = ["# Results", "", "Generated from `runs.jsonl` by `python -m evals.summarize`. Do not edit by hand.", ""]
    for (model_id, thinking, effort), rs in sorted(by_model.items()):
        passed = sum(r["passed"] for r in rs)
        out += [f"## {model_id} (thinking {thinking}, effort {effort})", "",
                f"**{passed}/{len(rs)} runs passed** ({100 * passed / len(rs):.0f}%) "
                f"across {len({r['task'] for r in rs})} tasks. "
                f"Total cost ${sum(r['cost_usd'] for r in rs):.4f}; "
                f"{sum(r['input_tokens'] for r in rs):,} input and {sum(r['output_tokens'] for r in rs):,} output tokens.", ""]

        added = sum(bool(r.get("tests_added")) for r in rs)
        if added:
            out += [f"{added} of {len(rs)} runs added tests (allowed; existing tests must be kept).", ""]
        out += ["| Difficulty | Passed |", "| --- | --- |"]
        for level in ("easy", "medium", "hard"):
            group = [r for r in rs if r["difficulty"] == level]
            if group:
                out.append(f"| {level} | {sum(r['passed'] for r in group)}/{len(group)} |")
        out.append("")

        out += ["| Task | Difficulty | Provokes | Passed | Calls (mean) | Input tokens (mean) | Cost (mean) | Stops | Why runs failed |",
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
                       f"{mean([r['input_tokens'] for r in trs]):,.0f} | ${mean([r['cost_usd'] for r in trs]):.4f} | "
                       f"{stops} | {why} |")
        out.append("")

        denied = Counter(d for r in rs for d in r["denials"])
        if denied:
            out += ["Commands denied (batch mode turns every ask into a deny):", ""]
            out += [f"- `{cmd}` ×{n}" for cmd, n in sorted(denied.items(), key=lambda kv: (-kv[1], kv[0]))]
            out.append("")
    return "\n".join(out)


def main():
    for results in sys.argv[1:]:
        path = ROOT / results / "summary.md"
        path.write_text(render(load_runs(ROOT / results)))
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
