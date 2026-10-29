# 03 - Safety

The thesis in one line: the model requests, the harness decides. This file is where the project's name comes from.

## Threat model

saysno runs model-chosen shell commands. The model is treated as untrusted, not because it is malicious but because it can be wrong, confused or steered by what it reads.

| Threat | Example | Control |
| --- | --- | --- |
| Destructive command | `rm -rf` outside the task, `git push --force`, `git reset --hard` | Allow/ask list (S-01), sandbox (S-03) |
| Cheating the task | Editing or deleting the failing test instead of fixing the code | Grader checks protected files (E-04); policy can deny edits to them (S-05) |
| Escaping the task | Reading or writing outside the working directory, network access | Path confinement (T-05), sandbox (S-03) |
| Prompt injection from files | A planted file says "ignore your instructions and run ..." | Same rules apply whatever the model says; tested with an injection task (E-06) |
| False "done" | Stopping without running the tests, or claiming they pass when they didn't run | Done gate (V-01), claim audit (V-02) |
| Runaway cost or loops | Retrying the same failing command, reading huge files repeatedly | Turn limit, token and cost budget (S-06, S-07) |
| Memory poisoning | A note the agent saved carries a bad instruction into the next run | Notes are task-local and shown in the transcript (C-07); out of scope beyond that |
| Leaking secrets | Printing environment variables into the transcript or a tool call | The sandbox gets no API key or credentials (S-04) |

## S - Safety and stopping

| ID | Requirement | Priority | Milestone | Status |
| --- | --- | --- | --- | --- |
| S-01 | `bash` commands are matched against an allow list (run), an ask list (confirm) and a default (ask); a denied call returns "denied" to the model with the reason | Must | M1 | *Done*: `test_allow_list_runs_without_asking`, `test_everything_else_asks`, `test_denied_command_is_reported_to_the_model_not_run` |
| S-02 | In batch eval runs there is no human: "ask" becomes "deny", and every denial is logged | Must | M2 | *Done*: `test_batch_run_denies_every_ask_and_records_the_run` |
| S-03 | Tools run in a sandbox: a Docker container with only the task directory mounted and no network. The model API call stays in the host process | Must | M4 | Planned |
| S-04 | The sandbox receives no API key, credentials or host environment | Must | M4 | Planned |
| S-05 | Files a task marks as protected (e.g. its tests) cannot be edited; the attempt is denied and logged | Should | M4 | Planned |
| S-06 | A turn limit ends the run with a clear "stopped: turn limit" outcome | Must | M4 | Planned |
| S-07 | A per-run token or cost budget ends the run with "stopped: budget" | Must | M4 | Planned |
| S-08 | An action log records every tool call, the decision (allow, ask, deny) and the rule that made it | Must | M4 | Planned |
| S-09 | The system prompt asks the model to run the tests before declaring done; the harness reports whether it did | Should | M4 | Planned |
| S-10 | Every S-area control has a test with the scripted model: a call it blocks and a nearby call it allows | Must | M4 | Planned |

## V - Verification

Implementation is cheap; knowing the change is right is not. S-09 asks the model to verify. The V controls move the check out of the model's hands: the harness decides whether "done" is supported, the same way it decides whether a command runs. Added at M7 in response to [F-03](../../results/m2/failure-log.md#f-03-done-without-running-the-tests): Haiku often said its fix was unverified, then stopped anyway, and every M2 failure came from a run that never ran the tests.

Each control asks a different question:

| Question | Answered by | Controls |
| --- | --- | --- |
| Was it checked? | The harness, from the action log | V-01, V-02 |
| Does the check mean anything? | A test that failed before the fix, or a reviewer that didn't write it | V-03, V-04 |
| What should a human look at? | The final report | V-05 |

| ID | Requirement | Priority | Milestone | Status |
| --- | --- | --- | --- | --- |
| V-01 | Done gate: when the model ends its turn and the task's test command has not passed since the last edit, the harness does not end the run; it tells the model what is missing. After 2 refusals the run ends with "stopped: unverified". A no-fix task (no edits) passes the gate | Must | M7 | Planned |
| V-02 | Claim audit: the final message's success claims ("tests pass", "fixed") are checked against the action log (S-08); a claim with no supporting tool call is flagged in the transcript and counted per run (E-07) | Must | M7 | Planned |
| V-03 | Reproduce first: when the agent adds a test, the harness runs it against the original code as well; the run records whether it failed before the fix and passes after | Should | M7 | Planned |
| V-04 | Independent reviewer: one model call with a fresh context sees the ticket, the diff and the test output, not the transcript, and returns approve or reject with a reason. On reject the agent gets the reason once. Same model as the agent, so the comparison is fresh context, not a stronger model | Should | M7 | Planned |
| V-05 | The final report lists what was checked, with the tool call that checked it, and what was not | Could | M7 | Planned |
| V-06 | Every V control has a test with the scripted model: a "done" it refuses or flags and a nearby one it accepts | Must | M7 | Planned |

## Residual risks

- **Allow lists are string matching.** A shell command can hide behaviour (`sh -c`, pipes, aliases). The sandbox (S-03) is the real boundary; the allow list is a speed bump that keeps the interactive mode usable. The post says so.
- **The sandbox is a container, not a VM.** Adequate for planted-bug tasks on a personal machine; not a claim about hostile code.
- **Verification is only as good as the tests.** The done gate checks that tests ran and passed, not that they cover the bug. V-03 and V-04 narrow the gap; E-14 measures what is left.
- **Before M4, runs are unsandboxed.** M1-M3 run only on the test bed, in a scratch copy, with the allow list and `ask` as default.
