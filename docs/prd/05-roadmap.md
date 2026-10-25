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

| ID | Requirement | Priority | Status |
| --- | --- | --- | --- |
| P-10 | Each milestone's last commit is tagged `m<n>`; each post links its tag | Must | Planned |

## Budget

| Item | Budget |
| --- | --- |
| Haiku runs, M1-M6 | Reported per post; stop and review if a milestone exceeds $10 |
| Opus runs, M7 | Estimated from Haiku token counts before running; confirm before spending |
| Whole series | Target under $50; actual reported in P-08 |

Development and CI use the scripted model. Any command that spends API credit is confirmed before it runs.

## Decisions (2026-10-25)

1. **Language: Python** for both the agent and the test bed. The 200-line loop stays readable, it is the language most agent-building roles use, and models are strongest in it, so failures come from the harness, not the language. Go was the alternative; planproof already shows Go.
2. **Test bed domain: a CSV report tool** ([04-evaluation.md](04-evaluation.md#test-bed)).
3. **Sandbox: Docker** (S-03). M1-M3 run without it, on a scratch copy of the test bed.
4. **Thinking: each model as people run it.** Haiku without thinking, Opus with adaptive thinking; the setting is recorded with every score (E-07). A fifth configuration (Opus without thinking) only if the four leave a question open.
5. **Tagged commits.** Each milestone's last commit is tagged `m1` ... `m7`, and each post links its tag so readers see the agent at that point (P-10).

## Open questions

None at M0.
