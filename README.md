# saysno

A minimal coding agent, built up one failure at a time, to show the harness, not the model, is what says no.

The model only requests actions; the program decides whether to run them. saysno starts as a bare agent loop in Python on the Anthropic SDK, runs it on planted-bug tasks, and adds one production feature per observed failure, scoring each. It ends by running the same tasks on a much stronger model, to see which features were crutches for a weak model and which are boundaries any model needs.

Status: planning. Start with the [PRD](docs/prd/README.md).

Each milestone is a post on [billykong.github.io](https://billykong.github.io).

## License

[MIT](LICENSE)
