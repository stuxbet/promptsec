# Defending an Internal AI Assistant Against Indirect Prompt Injection

[![ci](https://github.com/stuxbet/promptsec/actions/workflows/ci.yml/badge.svg)](https://github.com/stuxbet/promptsec/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/github/license/stuxbet/promptsec.svg)](LICENSE)

A lab-only cybersecurity project that simulates an internal AI assistant, exposes it to synthetic emails and documents containing **indirect prompt injection** attacks, and compares an intentionally vulnerable baseline against a layered defended pipeline.

Inspired by Google DeepMind's 2025 paper *Lessons from Defending Gemini Against Indirect Prompt Injections*.

## What it does

- Loads a synthetic corpus of emails and internal documents (some carrying hidden adversarial instructions).
- Runs each scenario through two assistant pipelines:
  - **Baseline** — naively merges user request + retrieved content into one prompt, no validation.
  - **Defended** — source labeling, prompt separation, tool allowlist, output validation, and a simulated approval gate for high-risk drafts.
- Scores both pipelines on attack success, benign task success, leakage, blocked unsafe actions, and false positives.
- Writes JSON, CSV, a Markdown comparison table, a matplotlib chart, and a PDF report.

## Requirements

- Python 3.11+
- A reachable **OpenAI-compatible** chat completions endpoint (e.g. local Ollama, LM Studio, vLLM, or a hosted provider). The project does not ship a mock model — a live LLM is required.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# edit .env to point at your endpoint
```

`.env` keys:

| key | meaning |
|---|---|
| `LLM_BASE_URL` | OpenAI-compatible base URL (e.g. `http://localhost:11434/v1`) |
| `LLM_MODEL` | model name served by that endpoint |
| `LLM_API_KEY` | optional, only if your endpoint requires it |
| `LLM_TIMEOUT_SECONDS` | per-request timeout |
| `OUTPUT_DIR` | where evaluation artifacts land (default `evidence/results`) |
| `LOG_LEVEL` | log verbosity |

## Usage

```bash
python -m src.cli.main seed-data                              # write synthetic fixtures
python -m src.cli.main run-baseline  --scenario-set default   # run the vulnerable assistant
python -m src.cli.main run-defended  --scenario-set default   # run the defended assistant
python -m src.cli.main evaluate      --scenario-set default   # both pipelines + metrics + report bundle
python -m src.cli.main generate-report-artifacts              # refresh Markdown + PDF report
```

`evaluate` writes:

- `evidence/results/comparison_summary.json` — machine-readable metrics
- `evidence/results/comparison.md` — human-readable summary table
- `evidence/results/comparison_chart.png` — bar chart
- `evidence/results/baseline_run.json`, `defended_run.json` — per-scenario logs

## Repo layout

```
src/
  app/         config + Pydantic models
  assistant/   baseline + defended pipelines, policy, validators, prompts
  cli/         Typer entry point
  data/        synthetic-data loader, retrieval, seeder
  evaluation/  scenario scoring, metrics, report writer
  llm/         OpenAI-compatible HTTP client
  tools/       simulated email/doc tools (no real side effects)
synthetic_data/   committed JSON fixtures (emails, docs, scenarios)
analysis/         threat model, asset inventory, baseline findings, residual risk
artifacts/        diagrams, matrices, checklists, test-case mappings
checkpoints/      staged course deliverables
evidence/         generated outputs (results, screenshots)
report/           final report (Markdown + PDF)
slides/           presentation outline
tests/            pytest suite
```

## Defenses, in one diagram

```
user request
   │
   ▼
retrieval ──► trust labels (trusted | untrusted | unknown)
   │
   ▼
prompt assembly  (system rules │ user intent │ retrieved data — kept separate)
   │
   ▼
model call ──► structured ModelResponse (action_name + content)
   │
   ▼
policy + validators
  ├─ tool allowlist            (summarize | draft_response | flag_for_review | refuse)
  ├─ leakage / hijack scan
  ├─ approval-bypass detector
  └─ request/output mismatch
   │
   ▼
approval gate for high-risk drafts
   │
   ▼
final response + run log
```

## Tests

```bash
pytest
```

Tests hit the configured live endpoint, so a model that doesn't exist or isn't running will fail the suite.

## Safety and ethics

- All data is synthetic; no real users, accounts, or systems are involved.
- Tools are simulated — no email is sent, no command is executed, no external request is made other than the model call itself.
- Scope is defensive: this repo demonstrates how to detect and block injection attempts, not how to launch them.

## License

MIT — see `LICENSE`.
