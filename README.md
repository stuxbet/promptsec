# Defending an Internal AI Assistant Against Indirect Prompt Injection

[![ci](https://github.com/stuxbet/promptsec/actions/workflows/ci.yml/badge.svg)](https://github.com/stuxbet/promptsec/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/github/license/stuxbet/promptsec.svg)](LICENSE)

## Team

- Luke Malcom

## Domain

AI security / applied cybersecurity — specifically, **indirect prompt injection**
defense for tool-using LLM assistants. Inspired by Google DeepMind's 2025 paper
*Lessons from Defending Gemini Against Indirect Prompt Injections*.

## Project description

A lab-only project that simulates an internal AI assistant, exposes it to synthetic
emails and documents containing hidden adversarial instructions, and compares an
intentionally vulnerable baseline against a layered defended pipeline.

The assistant is allowed to summarize, draft responses, flag for review, or refuse.
The baseline merges the user request with retrieved content into one prompt and
routes whatever action the model proposes. The defended pipeline keeps system
instructions, the user request, and retrieved data in separate channels with trust
labels, restricts the action surface, runs a battery of validators
([leakage scan, hijack-phrase scan, request/output mismatch, approval-bypass detector](src/assistant/validators.py)),
and routes high-risk drafts through a simulated approval gate.

Each scenario runs through both pipelines and is scored on attack success rate,
benign task success, leakage, blocked unsafe actions, and false positives.
Results land as JSON, CSV, a Markdown comparison table, a matplotlib chart, and
a PDF-ready report bundle.

## Tools used

| Layer | Tool |
|---|---|
| Language | Python 3.11+ |
| HTTP / LLM client | `httpx` against any OpenAI-compatible endpoint (Ollama, LM Studio, vLLM, hosted) |
| Data modeling | `pydantic` v2 |
| CLI | `typer` |
| Testing | `pytest` |
| Plotting | `matplotlib` |
| CI | GitHub Actions (syntax-check workflow + issue/PR templates under [`.github/`](.github/)) |
| VCS | git, GitHub |

No real tools are invoked — the email/doc tools under [src/tools/](src/tools/) are
simulated and produce no side effects beyond the model call itself.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env          # or: cp configs/env.example .env
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

- [`evidence/results/comparison_summary.json`](evidence/results/) — machine-readable metrics
- [`evidence/results/comparison.md`](evidence/results/comparison.md) — human-readable summary table
- [`evidence/results/metrics.png`](evidence/results/) — bar chart
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
configs/          environment-variable templates
checkpoints/      reserved for future fine-tuned weights (currently empty)
report/           final written report
slides/           presentation deck
evidence/         generated outputs (results, screenshots, validation table)
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

## Weekly progress summary

Dates are calendar weeks; commits are linked to track concrete deliverables.

- **Week of 2026-04-05** — Project initialized. Threat model, asset inventory,
  and baseline-findings docs drafted under [analysis/](analysis/). Synthetic
  email/doc/scenario fixtures committed under [synthetic_data/](synthetic_data/).
- **Week of 2026-04-12** — MVP shipped: baseline and defended assistants, scenario
  runner, metric calculator, Typer CLI. Fixed a freeze bug in the LLM client and
  added live status updates during benchmarks.
- **Week of 2026-04-25** — Removed mock-LLM scaffolding (a real endpoint is now
  required, matching the paper's evaluation realism). Rewrote project metadata,
  added community-health files (`SECURITY.md`, `CODE_OF_CONDUCT.md`,
  `CONTRIBUTING.md`, `CITATION.cff`), set up a GitHub Actions syntax-check
  workflow, and consolidated generated outputs under `evidence/results/`.
- **Week of 2026-04-26** (current) — Aligned the repository structure with the
  required layout (`checkpoints/`, `report/`, `slides/`, `configs/`) and expanded
  this README to cover team, domain, tools, progress, and outcomes.

## Final outcome summary

Across 21 scenarios (8 benign, 4 edge, 9 malicious indirect-prompt-injection
attempts), the defended pipeline closed every successful attack the baseline let
through without sacrificing benign-task success. Numbers from
[`evidence/results/comparison.md`](evidence/results/comparison.md):

| Pipeline | Attack success | Benign success | Leakage | Blocked unsafe | False positives |
|---|---:|---:|---:|---:|---:|
| Baseline  | **0.700** | 1.000 | 0.190 | 0.100 | 0.000 |
| Defended  | **0.000** | 1.000 | 0.000 | 1.000 | 0.000 |

Concretely, the baseline followed injected instructions to leak confidential
tokens (`BUDGET-421`, `CUST-8891`, `AP-7719`), draft approval-bypass replies, and
propose `export_data` / `run_command`. The defended pipeline either refused
those actions outright (action allowlist), blocked them at validation
(leakage / suspicious-phrase / hijack scans), or routed them to the simulated
approval gate. Benign and edge scenarios passed through unchanged in both
pipelines, so the layered defense added no measurable false-positive cost on
this corpus.

The result echoes the paper's §10 takeaway: a single defense is not enough, but
**defense in depth** at the system level meaningfully shrinks the indirect-prompt-injection
attack surface — even without adversarial fine-tuning of the underlying model.

## Tests

```bash
pytest
```

Tests hit the configured live endpoint, so a model that isn't running will fail
the suite.

## Safety and ethics

- All data is synthetic; no real users, accounts, or systems are involved.
- Tools are simulated — no email is sent, no command is executed, no external
  request is made other than the model call itself.
- Scope is defensive: this repo demonstrates how to detect and block injection
  attempts, not how to launch them.

## License

MIT — see [`LICENSE`](LICENSE).
