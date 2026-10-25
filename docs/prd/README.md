# Product requirements: saysno

This folder is the product requirements document (PRD): what we're building, why, the requirements each part must meet, and how we'll know it works.

## Documents

| Document | Contents |
| --- | --- |
| [01-overview.md](01-overview.md) | Problem, product, thesis, goals and non-goals, design principles, success measures |
| [02-architecture.md](02-architecture.md) | The loop, the tools, context and memory: areas L, T and C |
| [03-safety.md](03-safety.md) | Permissions, sandbox, stopping, threat model: area S |
| [04-evaluation.md](04-evaluation.md) | Test bed, task set, scoring, model comparison: area E |
| [05-roadmap.md](05-roadmap.md) | Milestones, the blog series (area P), open questions |

## Status at a glance

| Milestone | Status |
| --- | --- |
| M0: PRD | **Done** (2026-10-25): open questions decided |
| M1: Bare loop | Planned |
| M2: Test bed and evaluation | Planned |
| M3: Cheap context wins | Planned |
| M4: Stopping and safety | Planned |
| M5: Compaction | Planned |
| M6: Memory | Planned |
| M7: Model comparison | Planned |

## Conventions

- **Requirement IDs** take the form `<area>-<nn>`, e.g. `L-03` or `S-02`. IDs are stable: a dropped requirement is marked *Dropped*, never renumbered.
- **Areas:** L loop, T tools, C context and memory, S safety, E evaluation, P posts.
- **Priority:** **Must** (the project isn't done without it), **Should** (expected; omission needs a stated reason) or **Could** (nice to have).
- **Status:** *Done* (an automated test proves it, and the test is named), *Partial*, *Planned* or *Open question*.
- "Done" means demonstrated by a test in this repo. A requirement met only by something nothing checks is *Partial*.
- Update this PRD in the same commit as the change that alters a requirement's status. Generate scores and costs from the eval runs; don't type them in.
