# Security Policy

This is a lab/educational project. The code is intentionally vulnerable in places (the **baseline assistant**) so that the defended pipeline has something to compare against. Do not deploy any part of this repo against real users, real data, or real production systems.

## Reporting a vulnerability

If you find a real security issue in the **defended** code path or in any tooling that could be exploited outside the lab context, please report it privately rather than opening a public issue.

- Open a private vulnerability report via GitHub: https://github.com/stuxbet/promptsec/security/advisories/new
- Or email the maintainer: see the email in the latest commit metadata.

Please include:
- A short description of the issue.
- Steps to reproduce, or a minimal proof of concept.
- The affected file path and (if known) the commit SHA.

## What's in scope

- The defended assistant pipeline (`src/assistant/defended.py`, validators, policy, approval gate).
- The CLI entrypoint (`src/cli/main.py`).
- Anything in `src/llm/` that talks to the model endpoint.

## What's out of scope

- The baseline assistant (`src/assistant/baseline.py`) — it is **intentionally vulnerable** for comparison.
- Synthetic fixtures under `synthetic_data/` containing crafted adversarial content.
- Reports in `report/` and `evidence/` that quote vulnerable behavior.

## Disclosure

I'll aim to acknowledge reports within a week and follow up with a fix or a "won't fix, here's why" within two weeks. This is a one-person project; response times are best-effort.
