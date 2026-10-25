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
| Runaway cost or loops | Retrying the same failing command, reading huge files repeatedly | Turn limit, token and cost budget (S-06, S-07) |
| Memory poisoning | A note the agent saved carries a bad instruction into the next run | Notes are task-local and shown in the transcript (C-07); out of scope beyond that |
| Leaking secrets | Printing environment variables into the transcript or a tool call | The sandbox gets no API key or credentials (S-04) |

## S - Safety and stopping

| ID | Requirement | Priority | Milestone | Status |
| --- | --- | --- | --- | --- |
| S-01 | `bash` commands are matched against an allow list (run), an ask list (confirm) and a default (ask); a denied call returns "denied" to the model with the reason | Must | M1 | Planned |
| S-02 | In batch eval runs there is no human: "ask" becomes "deny", and every denial is logged | Must | M2 | Planned |
| S-03 | Tools run in a sandbox: a container with only the task directory mounted and no network. The model API call stays in the host process | Must | M4 | Planned |
| S-04 | The sandbox receives no API key, credentials or host environment | Must | M4 | Planned |
| S-05 | Files a task marks as protected (e.g. its tests) cannot be edited; the attempt is denied and logged | Should | M4 | Planned |
| S-06 | A turn limit ends the run with a clear "stopped: turn limit" outcome | Must | M4 | Planned |
| S-07 | A per-run token or cost budget ends the run with "stopped: budget" | Must | M4 | Planned |
| S-08 | An action log records every tool call, the decision (allow, ask, deny) and the rule that made it | Must | M4 | Planned |
| S-09 | The system prompt asks the model to run the tests before declaring done; the harness reports whether it did | Should | M4 | Planned |
| S-10 | Every S-area control has a test with the scripted model: a call it blocks and a nearby call it allows | Must | M4 | Planned |

## Residual risks

- **Allow lists are string matching.** A shell command can hide behaviour (`sh -c`, pipes, aliases). The sandbox (S-03) is the real boundary; the allow list is a speed bump that keeps the interactive mode usable. The post says so.
- **The sandbox is a container, not a VM.** Adequate for planted-bug tasks on a personal machine; not a claim about hostile code.
- **Before M4, runs are unsandboxed.** M1-M3 run only on the test bed, in a scratch copy, with the allow list and `ask` as default.
