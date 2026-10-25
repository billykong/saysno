# M1 results

One interactive run of the bare loop on `examples/first-task`, Claude Haiku 5.5 (thinking off, effort high), 2026-10-25. Transcript: [first-task-haiku.jsonl](first-task-haiku.jsonl).

- **Outcome:** fixed. `mean()` divided by `len(values) - 1`; the agent changed it to `len(values)` and ran the tests (3 passed).
- **Model calls:** 4. **Tokens:** 5,369 input, 569 output, 0 cache reads. **Cost:** about $0.0008.
- **Tool calls:** `grep`, `bash` (`ls -R | head -100`: asked because of the pipe, denied), `read_file`, `edit_file`, `bash` (`python -m pytest -q`: allowed).
- **Seen:** the denial cost nothing; the model said `grep` had already told it enough and moved on. A single run on an easy task shows the loop works, not how well; scores start in M2.
