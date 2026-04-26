# configs/

Configuration templates for running the pipelines.

- [`env.example`](env.example) — copy to `.env` at the repo root and edit to point
  at your LLM endpoint. Mirrors the canonical `.env.example` at the project root.

Runtime knobs (LLM endpoint, model name, timeout, output directory, log level)
are all environment-variable driven; see the README for the full key list.
