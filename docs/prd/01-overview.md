# 01 - Overview

## Problem

Coding agents are now everyday tools, and "how does one actually work?" is a common interview question and take-home exercise. The usual answer, "it's a loop around a model", is true but misleading:

1. **The loop is small; the harness is not.** A bare agent is 100-200 lines. What separates it from a production agent is context management, permissions, stopping and evaluation, and most write-ups stop before those.
2. **Better models invite the wrong conclusion.** Each model generation makes a bare loop look more capable, which suggests the harness is scaffolding that will soon be unnecessary. Some of it is. Some of it never will be, and the difference is rarely measured.

## Product

**saysno is a minimal coding agent in Python on the Anthropic SDK, built up one failure at a time, with a blog series that measures what each addition is for.**

- Start with the bare loop and four tools.
- Run it on a fixed set of planted-bug tasks and record every failure.
- Add one production feature per observed failure, and rescore after each.
- End by running the same tasks on a much stronger model, with and without the harness.

Each milestone is a blog post on [billykong.github.io](https://billykong.github.io).

## Thesis

**The harness is the only thing that says no.** The model only requests actions; the program decides whether to run them. Every production feature refines one of the loop's four stages. Features that compensate for a weak model (tool-use help, self-correction hints) lose value as models improve. Features that set boundaries (permissions, cost, stopping, evaluation) do not: a smarter model is still not an authority on what it may run, costs more per token, and can be confidently wrong.

The agent is the demo. The argument is the product.

## Audience

| Who | What they need from it |
| --- | --- |
| Engineers preparing for agent-building roles or interviews | A readable loop and a clear map of what production adds |
| Engineers building internal agents | Measured evidence of which harness features matter, and for which model |
| Hiring managers and reviewers | Evidence the author understands the hard parts, not only the loop |
| The author | A public write-up of skills built on a work agentic support/DevOps system, without exposing work code |

## Goals

1. **G1 - A loop people can read.** The M1 agent fits on one screen pair: at most 200 non-blank, non-comment lines, one third-party dependency (the Anthropic SDK).
2. **G2 - Every addition earns its place.** Each feature after M1 is added in response to a failure recorded in the failure log, and comes with a score before and after.
3. **G3 - Measure, don't anecdote.** A fixed task set with planted bugs, scored automatically, after every change.
4. **G4 - Answer the model question.** The final comparison classifies every feature as a **crutch** (helps a weak model, not a strong one) or a **boundary** (needed with any model), with the numbers.
5. **G5 - A series people finish.** Short posts, one per milestone, each readable on its own.

## Non-goals

- **Competing with Claude Code** or any production agent.
- **A framework or library.** No plugin system, no configuration language. Copy-and-read code.
- **Agent frameworks.** The Anthropic SDK only, so the loop is visible; no Agent SDK, LangChain or similar.
- **Real-world repositories as the benchmark.** Planted bugs give known answers; real bugs are noisy.
- **Multiple model providers.** Claude models only, so comparisons isolate model capability, not API differences.
- **A UI.** A terminal REPL and a batch eval runner.

## Design principles

1. **Trust the harness, not the model.** The model's tool calls are requests. Only the harness decides what runs.
2. **Fail loudly.** Tools return clear errors (no match, several matches, truncated output) rather than doing something plausible.
3. **One failure, one feature.** No feature is added speculatively. Each cites the failure-log entry that motivated it.
4. **Same tasks, same scorer.** The task set changes only by adding tasks; scores across milestones stay comparable.
5. **Report what didn't help.** A feature that doesn't move the score, or stops mattering on Opus, is reported, not hidden.
6. **Cheap to reproduce.** A scripted model replays tool calls so the loop and tools are tested in CI without an API key or a bill.

## Success measures

| Measure | Target |
| --- | --- |
| M1 agent size (non-blank, non-comment Python lines) | At most 200 |
| Agent size at each milestone | Reported per post |
| Features added without a failure-log entry | 0 |
| Eval score per milestone, per model | Reported, generated from runs |
| Unsafe actions run without confirmation (eval runs) | 0 after M4 |
| Total API spend for the series | Reported per post; budget in [05-roadmap.md](05-roadmap.md) |
| Final comparison | Every feature classified crutch or boundary, with the numbers |
