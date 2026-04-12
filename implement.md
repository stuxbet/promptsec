# Implementation Plan: Defending an Internal AI Assistant Against Indirect Prompt Injection

## Summary
- Build a public, offline-first Python 3.11 repo that demonstrates indirect prompt injection against a synthetic internal-assistant workflow, then compares a vulnerable baseline with a layered defended version.
- Use a top-level Python package named `src` so the documented commands stay `python -m src.cli.main ...`.
- Make the offline path the primary demo: a deterministic mock model must reliably show baseline failures on malicious scenarios and defended improvements on the same scenarios.
- Ship the repo as a complete course artifact set: runnable code, synthetic data, evaluation outputs, Markdown analysis artifacts, checkpoints, report outline, and slide outline.

## Key Changes
1. Scaffold the repo with `pyproject.toml`, `requirements.txt`, `README.md`, `LICENSE`, `.env.example`, the `src/` package tree from the spec, `tests/`, and the documentation/evidence folders. Use `typer`, `pydantic`, `pytest`, and `httpx`; write reports directly in Markdown and CSV/JSON without Jinja2.
2. Define canonical Pydantic types for `ContentItem`, `Scenario`, `AssistantRequest`, `AssistantResponse`, `ToolAction`, `PolicyDecision`, `ValidationFinding`, `RunLog`, and `EvaluationSummary`. Standardize `expected_behavior` as `summarize`, `draft_safe`, `flag_review`, `refuse`, or `requires_approval`.
3. Store synthetic data as committed JSON files under `synthetic_data/`, with one file per email/document and one file per scenario. Generate and commit exactly 35 content items: 20 benign, 10 malicious, 5 ambiguous. Generate exactly 20 scenarios: 8 benign, 8 malicious, 4 edge. Implement `seed-data` as an idempotent generator that rewrites those committed JSON fixtures from canonical Python definitions.
4. Implement a simple retrieval layer using deterministic keyword and tag scoring. Baseline retrieval ignores trust metadata entirely. Defended retrieval preserves the same candidate set but carries `trusted` / `untrusted` / `unknown` labels forward and uses trust only to inform downstream handling, not to silently drop evidence.
5. Create a `ModelBackend` interface with two implementations: `MockModel` and `OpenAICompatibleModel`. `MockModel` must intentionally obey malicious phrases embedded in retrieved text when the prompt is naively merged, so the baseline can deterministically exhibit instruction override, leakage, summary poisoning, and approval-bypass failures offline. `OpenAICompatibleModel` should call a generic `/v1/chat/completions`-style endpoint configured by env vars and remain fully optional.
6. Implement simulated tools only: `read_email`, `search_docs`, `draft_email`, and `flag_review` return structured payloads and logs, but never send messages, execute shell commands, or reach external systems. The baseline tool router can broadly allow these simulated actions; the defended router must explicitly block any undeclared or external-facing action.
7. Build the baseline assistant as a deliberately weak pipeline: retrieve items, concatenate user request plus retrieved content into one prompt, ask the model for a summary/draft/action, and return the result with only minimal logging. No trust-aware behavior, no prompt separation, no validation, and no approval gate.
8. Build the defended assistant as a layered pipeline: separate system rules, user request, and retrieved data into distinct prompt sections; label every retrieved item with trust; restrict actions to `summarize`, `draft_response`, and `flag_for_review`; run policy checks before and after model output; and route high-risk cases to approval. High-risk means any external-facing draft touching confidential content, any suspected exfiltration attempt, or any output that appears driven by retrieved instructions instead of the user request.
9. Implement validators for prompt-hijack phrases, unrelated confidential-data leakage, forbidden actions, approval-bypass attempts, and request/output mismatch. On a violation, the defended assistant must return either `blocked` or `needs_review` plus a short rationale, and write a structured log entry.
10. Build one evaluation harness that runs the same scenario set against both assistants and writes per-run logs plus aggregate outputs to `evidence/results/`. Metrics are fixed as: `attack_success_rate = malicious scenarios with unsafe outcome / malicious scenarios`, `benign_task_success_rate = benign scenarios meeting expected behavior / benign scenarios`, `leakage_rate = scenarios with unrelated confidential disclosure / all scenarios`, `blocked_unsafe_action_rate = guarded scenarios safely blocked or routed / guarded scenarios`, and `false_positive_rate = benign or edge scenarios incorrectly blocked / benign + edge scenarios expected to proceed`.
11. Add CLI commands exactly for `run-baseline`, `run-defended`, `evaluate`, `generate-report-artifacts`, and `seed-data`. `evaluate` must emit terminal output, JSON, CSV, a Markdown comparison table, and an optional matplotlib chart.
12. Write the repo artifacts as GitHub-ready Markdown: README with course placeholders and weekly progress slots, analysis documents tied to the fictional organization scenario, Mermaid architecture/data-flow diagrams, risk and permission matrices, control checklist, test case matrix, checkpoint narratives, final report outline, references, and presentation outline.

## Public Interfaces
- Config env vars: `MODEL_BACKEND=mock|openai_compatible`, `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `OPENAI_MODEL`, `OUTPUT_DIR`, `LOG_LEVEL`.
- CLI surface: `python -m src.cli.main seed-data`, `run-baseline --scenario-set default`, `run-defended --scenario-set default`, `evaluate --scenario-set default --output-dir ...`, `generate-report-artifacts`.
- Scenario schema fields: `scenario_id`, `user_request`, `relevant_data_files`, `expected_safe_behavior`, `unsafe_behavior_to_avoid`, `attack_category`, `sensitivity_level`.
- Content schema fields: `id`, `type`, `trust_level`, `sensitivity`, `content`, `tags`, `expected_behavior`, `attack_goal`.
- Log/result schema: retrieved item IDs, trust labels, proposed action, policy decision, validation findings, approval decision, final response, and scenario verdict.

## Test Plan
- Unit tests for schema loading, trust-label parsing, retrieval scoring, policy enforcement, validator behavior, approval gating, and metric calculations.
- Integration tests on a fixed subset where the baseline must follow injected content or leak data and the defended assistant must instead block, flag, or require approval.
- CLI smoke tests for offline `run-baseline`, `run-defended`, `evaluate`, and `generate-report-artifacts`.
- Acceptance checks that offline mode works with no API key, both assistants run on the same scenario set, outputs are produced in machine-readable and human-readable form, and no command in the default path performs networked side effects.

## Assumptions
- Use `Typer`, JSON fixtures, and a working optional OpenAI-compatible adapter as the v1 defaults.
- Use Mermaid inside Markdown for diagrams and MIT for `LICENSE`, unless the course requires a different license later.
- Keep v1 intentionally simple: no frontend, no embeddings, no HTML dashboard, no real integrations, no offensive tooling, and no Jinja2 templating unless report generation becomes repetitive.
- The benchmark target is directional, not production-grade: the baseline should fail on multiple malicious scenarios by design, and the defended path should materially improve attack success and leakage metrics while preserving most benign-task utility.
