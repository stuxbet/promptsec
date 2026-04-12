# Defending an Internal AI Assistant Against Indirect Prompt Injection

An offline-first cybersecurity class project that simulates a fictional internal AI assistant, measures how it behaves when synthetic emails and documents contain indirect prompt injection attacks, and compares a vulnerable baseline against a defended pipeline.

## Team
- Team Member 1: `TBD`
- Team Member 2: `TBD`
- Team Member 3: `TBD`

## Project Domain
Approved domain: `AI Agent Security`

Scope: a defensive, lab-only evaluation of a tool-using internal AI assistant that retrieves company content and is exposed to indirect prompt injection risk.

## Project Window And Milestones
- Project window: April 1 to April 30
- Checkpoint 1 due: April 5
- Checkpoint 2 due: April 12
- Checkpoint 3 due: April 19
- Checkpoint 4 and final report due: April 26
- Presentation dates: May 5 and May 7

## Organization Scenario
A fictional company is piloting an internal AI assistant to help staff read emails, search internal policies, summarize results, draft replies, and flag risky items for review. The organization wants to understand how indirect prompt injection in retrieved content can cause unsafe automation, leakage, or approval bypass.

## Project Description
This repo demonstrates a lab-only scenario inspired by Google DeepMind's 2025 paper, *Lessons from Defending Gemini Against Indirect Prompt Injections*. The assistant can read synthetic emails, search synthetic internal documents, summarize findings, draft replies, and flag items for review. The baseline path is intentionally weak. The defended path applies layered controls, validation, and simulated human approval for high-risk actions.

## Team Roles
- Project lead: `TBD`
- Risk / threat analyst: `TBD`
- Technical implementation / validation lead: `TBD`
- Documentation / presentation lead: `TBD`

## Tools Used
- Python 3.11+
- Typer CLI
- Pydantic
- pytest
- httpx for optional OpenAI-compatible API access
- matplotlib for comparison charts and PDF report export
- Mermaid diagrams in Markdown

## Safety And Ethics
- All data is synthetic.
- No real users or systems are targeted.
- No public services are tested by the offline workflow.
- No real secrets are used.
- No offensive exploitation is performed.
- All actions are simulated or sandboxed for defensive education and research.

## Repo Structure
- `src/`: application code for assistants, retrieval, evaluation, tools, and CLI.
- `synthetic_data/`: JSON fixtures for emails, documents, and scenarios.
- `analysis/`: threat model, baseline findings, asset inventory, and residual risk.
- `artifacts/`: diagrams, matrices, checklists, and test-case mappings.
- `checkpoints/`: staged course deliverables.
- `report/`: final report outline, references, and appendix index.
- `slides/`: presentation outline.
- `evidence/`: generated outputs, result tables, and screenshots.

## Quickstart
1. Create a Python 3.11+ environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Seed the synthetic dataset with `python -m src.cli.main seed-data`.
4. Run the baseline with `python -m src.cli.main run-baseline --scenario-set default`.
5. Run the defended assistant with `python -m src.cli.main run-defended --scenario-set default`.
6. Compare both paths with `python -m src.cli.main evaluate --scenario-set default --output-dir evidence/sample_outputs`.
7. Optional live API mode: set `LLM_MODE=http` and `LLM_BASE_URL` to an OpenAI-compatible endpoint. Offline mode is the default and does not require network access.

## Experiment Workflow
- Offline mode is the default and uses a deterministic mock model.
- Optional OpenAI-compatible integration is available by setting `LLM_MODE=http` and `LLM_BASE_URL`.
- Evaluation writes machine-readable JSON and CSV, a Markdown summary table, and a comparison chart.
- `python -m src.cli.main generate-report-artifacts` refreshes the final report bundle in Markdown and PDF.

## Course Deliverables Mapping
- Project title and domain: covered here in the README header and project-domain section.
- Team member names: listed under the Team section.
- Tools used: listed in the Tools Used section.
- Weekly progress summary: listed below and mirrored in `checkpoints/`.
- Final outcome summary: generated outputs are stored in `evidence/sample_outputs/` and summarized in `analysis/` and `report/`.

## Weekly Progress Summary
- Week 1 / Checkpoint 1: scope, architecture, and asset inventory finalized.
- Week 2 / Checkpoint 2: threat model and vulnerable baseline completed.
- Week 3 / Checkpoint 3: layered defenses and initial evaluation completed.
- Week 4 / Checkpoint 4: refined results, residual risk, report bundle, and presentation artifacts completed.

## Current Evaluation Snapshot
- Baseline attack success rate: `0.700`
- Defended attack success rate: `0.000`
- Baseline leakage rate: `0.190`
- Defended leakage rate: `0.000`
- Baseline benign task success rate: `1.000`
- Defended benign task success rate: `1.000`

## Final Outcome Summary
The current offline evaluation shows that the defended assistant materially reduces attack success and leakage relative to the intentionally vulnerable baseline while preserving benign task success across the scenario set. The repo includes the required analysis artifacts, checkpoints, evidence outputs, a report bundle, and presentation scaffolding for the course project.
# promptsec
