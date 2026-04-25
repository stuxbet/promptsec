# Contributing

Thanks for your interest. This is a small lab/educational project, but contributions are welcome.

## Before you start

- Open an issue first for anything larger than a typo or a one-line fix, so we can agree on direction before you write code.
- Keep the project's defensive scope in mind: this repo demonstrates how to **detect and block** indirect prompt-injection attempts, not how to launch them. New attack scenarios in `synthetic_data/` are fine; new exploitation tooling against real systems is not.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# point .env at a reachable OpenAI-compatible endpoint
```

Run the pipeline end-to-end:

```bash
python -m src.cli.main seed-data
python -m src.cli.main evaluate --scenario-set default
```

## Tests

```bash
pytest
```

The current test suite calls the configured live LLM endpoint, so a model that isn't running will fail the suite.

## Style

- Python 3.11+, type-annotate new code.
- Keep functions small and pure where possible.
- No comments that just restate what the code does.

## Commit messages

Use conventional-commit prefixes:

- `feat:` user-visible new behavior
- `fix:` bug fix
- `docs:` docs only
- `chore:` housekeeping
- `ci:` CI config changes
- `refactor:` no behavior change

Keep the subject under 72 characters. Use the body to explain *why*, not what.

## Pull requests

- One logical change per PR.
- Include a short test plan in the PR body.
- Link related issues.
