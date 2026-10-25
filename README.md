# saysno

A minimal coding agent, built up one failure at a time, to show the harness, not the model, is what says no.

The model only requests actions; the program decides whether to run them. saysno starts as a bare agent loop in Python on the Anthropic SDK, runs it on planted-bug tasks, and adds one production feature per observed failure, scoring each. It ends by running the same tasks on a much stronger model, to see which features were crutches for a weak model and which are boundaries any model needs.

Status: M1, the bare loop. Start with the [PRD](docs/prd/README.md).

## Run it

Needs Python 3.12+, [uv](https://docs.astral.sh/uv/) and an Anthropic API key in `ANTHROPIC_API_KEY`. Work on a copy: the agent edits files and, with your yes, runs commands.

```bash
cp -r examples/first-task /tmp/first-task
uv run saysno --dir /tmp/first-task "$(cat /tmp/first-task/TASK.md)"
```

`--model opus` switches from Claude Haiku 5.5 to Claude Opus 5.5. Each run writes a transcript to `transcripts/`.

Tests use a scripted model and need no key: `uv run pytest`.

Each milestone is a post on [billykong.github.io](https://billykong.github.io).

## License

[MIT](LICENSE)
