# 05 - Roadmap

## Sequencing

```mermaid
flowchart LR
  M0["M0: PRD"] --> M1["M1: Bare loop"]
  M1 --> M2["M2: Test bed and evaluation"]
  M2 --> M3["M3: Cheap context wins"]
  M3 --> M4["M4: Stopping and safety"]
  M4 --> M5["M5: Compaction"]
  M5 --> M6["M6: Memory"]
  M6 --> M7["M7: Model comparison"]
```

Evaluation comes second, not last, so every later milestone reports a score change. M3-M6 are the expected order; the failure log may reorder them or add one.

| Milestone | Scope | Exit criteria |
| --- | --- | --- |
| M0 | This PRD | Reviewed; open questions below answered or deferred |
| M1 | Loop, four tools, allow/ask list, scripted model, transcript (L-01 to L-06, T-01 to T-05, S-01) | Fixes one task interactively on Haiku; CI green without an API key; at most 200 lines |
| M2 | Test bed, tasks, runner, scorer, failure log (E-01 to E-11, S-02) | Bare loop scored on Haiku, 3 runs; failure log populated |
| M3 | Output cap, just-in-time loading, cache-friendly prompt (C-01 to C-03, L-07) | Score and tokens before and after, on Haiku |
| M4 | Sandbox, protected files, turn limit, budget, action log, verify-before-done (S-03 to S-10, E-06) | Every S control has a block and an allow test; 0 unconfirmed unsafe actions in runs |
| M5 | Compaction (C-04, C-05) | The long task completes with compaction; one documented failure case |
| M6 | Instruction file, progress notes (C-06, C-07) | Score before and after; a run that resumes from notes |
| M7 | Model comparison and ablation (E-20 to E-22) | Every feature classified crutch or boundary |

## P - Posts

One short post per milestone on [billykong.github.io](https://billykong.github.io), each readable on its own, each naming the loop stage it changes and the numbers that justify it.

| ID | Post | After | Priority |
| --- | --- | --- | --- |
| P-01 | Overview: a coding agent is a loop; the memory and context ladders | M0 | Must |
| P-02 | The loop is 200 lines; everything else is the harness | M1 | Must |
| P-03 | What a bare loop gets wrong: the first scores and the failure log | M2 | Must |
| P-04 | Cheap context wins | M3 | Should |
| P-05 | The harness is the only thing that says no | M4 | Must |
| P-06 | Compaction, and the detail it dropped | M5 | Should |
| P-07 | Memory: what an agent should write down | M6 | Should |
| P-08 | Does a better model make the harness pointless? | M7 | Must |
| P-09 | Retrospective, in `billy-notes` | M7 | Should |

Posts P-04, P-06 and P-07 may merge if a milestone's result is small.

## Budget

| Item | Budget |
| --- | --- |
| Haiku runs, M1-M6 | Reported per post; stop and review if a milestone exceeds $10 |
| Opus runs, M7 | Estimated from Haiku token counts before running; confirm before spending |
| Whole series | Target under $50; actual reported in P-08 |

Development and CI use the scripted model. Any command that spends API credit is confirmed before it runs.

## Open questions

1. **Test bed domain.** What the planted-bug project does (a CSV/report tool, a small inventory service, a text parser). It should have several modules so some bugs are far from their symptoms.
2. **Sandbox tool.** Docker or Podman, and whether M1-M3 also run in it from the start.
3. **Thinking.** Whether to use extended thinking on Opus in M7, and if so, report it as a fifth configuration.
4. **Post format.** Whether each post links a tagged commit (`m1`, `m2`, ...) so readers can see the agent at that point.
