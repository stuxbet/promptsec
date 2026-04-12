Use this as the prompt/spec for Codex.

This repo spec is aligned to your course brief, which requires a public GitHub repo with steady progress plus a threat model, defensive controls, validation, before/after comparison, residual risk, and supporting artifacts. It is also grounded in Google DeepMind’s 2025 paper on indirect prompt injection in tool-using AI systems and their layered-defense/evaluation approach. ([arXiv][1])

---

# Repo spec for Codex

Create a complete, clean, lab-only GitHub repository for a defensive cybersecurity class project titled:

**Defending an Internal AI Assistant Against Indirect Prompt Injection**

## Objective

Build a reproducible research/demo repo that simulates an internal company AI assistant which reads synthetic emails and documents, then evaluates how vulnerable it is to **indirect prompt injection** attacks. The repo must include:

- a vulnerable baseline assistant
- a defended assistant with layered controls
- a synthetic dataset of benign and malicious documents/emails
- an evaluation harness that compares baseline vs defended performance
- diagrams, evidence, checkpoints, report scaffolding, and slides scaffolding

The entire repo must stay **defensive, lab-only, and safe**:

- no real email sending
- no real credentials
- no public-target testing
- no external system exploitation
- only synthetic data
- any tool actions must be simulated or sandboxed

The repo should be designed so a student team can use it for a one-month course project and presentation. The course brief explicitly requires a public repo, steady checkpoints, asset inventory, threat model, defensive controls, validation/evaluation, before-vs-after comparison, residual risk, and organized materials.

## Research framing

The repo should clearly state that it is inspired by Google DeepMind’s paper **“Lessons from Defending Gemini Against Indirect Prompt Injections”**, which describes indirect prompt injection as malicious instructions embedded in untrusted data sources that a model later retrieves and uses, and emphasizes adversarial evaluation plus layered defenses. ([arXiv][1])

## Tech stack

Use a simple stack that is easy for students to run:

- Python 3.11+
- pytest
- pydantic
- typer or argparse for CLI
- Jinja2 optional for report template generation
- matplotlib optional for charts
- no heavy frontend required
- no dependency on paid APIs for core functionality

Design the repo so it runs in two modes:

### Mode 1: fully offline demo mode

Use a deterministic local “simulated model” or rule-based responder so the repo works without API keys.

### Mode 2: pluggable LLM backend

Allow optional integration with an OpenAI-compatible API via environment variable, but keep this optional and clearly separated behind an interface.

The project must still be useful and demonstrable in offline mode.

## Core scenario

Simulate a fictional company assistant that can:

- read synthetic emails
- search synthetic internal documents
- summarize results
- draft an email reply
- flag an item for review

The assistant must **not** actually send emails or take real-world actions.

The key security problem is that malicious instructions may be hidden inside retrieved emails or documents. This is the indirect prompt injection threat model described in the Google DeepMind work. ([arXiv][1])

## Required features

### 1. Synthetic dataset

Create a small but realistic synthetic dataset with:

- 15 to 25 benign emails/documents
- 10 to 15 malicious or adversarial emails/documents
- 5 ambiguous edge cases

Organize them into JSON or YAML files with metadata:

- id
- type: email or doc
- trust_level: trusted, untrusted, unknown
- sensitivity: public, internal, confidential
- content
- tags
- expected_behavior
- attack_goal if malicious

Examples:

- benign HR benefits email
- benign reimbursement policy
- benign onboarding checklist
- malicious email containing hidden instruction to ignore user intent
- malicious doc attempting to cause data exfiltration
- malicious content trying to trigger unsafe drafting behavior

### 2. Baseline vulnerable assistant

Implement a baseline assistant pipeline that:

- takes a user request
- retrieves relevant synthetic items
- passes them to the model layer
- returns a summary or draft response

This baseline should intentionally be weak:

- no strong separation of instructions vs retrieved content
- no output validation
- no trust-aware retrieval behavior
- broad tool permissions within the sandbox

The goal is to make the baseline plausibly vulnerable for comparison.

### 3. Defended assistant

Implement a defended pipeline with layered controls:

#### A. source labeling

Retrieved content is explicitly labeled as trusted/untrusted/unknown.

#### B. prompt separation

System instructions, user intent, and retrieved data must be clearly separated.

#### C. tool restrictions

Allowed actions:

- summarize
- draft response
- flag for review

Disallowed:

- real sends
- arbitrary command execution
- any networked external side effects

Add a policy layer so risky actions are blocked or routed to approval.

#### D. output validation

Implement checks for:

- unrelated sensitive data leakage
- attempts to follow instructions from retrieved content instead of user intent
- forbidden actions
- suspicious phrases indicating prompt hijacking

#### E. human approval gate

For high-risk actions such as drafting an external-facing message involving confidential content, require explicit approval in the simulation before the action is considered successful.

### 4. Evaluation harness

Create a repeatable evaluation framework that runs a scenario set against both:

- baseline assistant
- defended assistant

Metrics should include:

- attack success rate
- benign task success rate
- leakage rate
- blocked unsafe action rate
- false positive / overblocking rate
- per-scenario notes

Output:

- terminal summary
- CSV or JSON results
- a simple markdown report table
- optional chart image

### 5. Threat model and analysis artifacts

Include static artifacts in the repo:

- asset inventory
- threat model
- risk matrix
- access-control / permission matrix
- data flow diagram
- architecture diagram
- control checklist
- test case matrix
- residual risk summary

### 6. Checkpoint materials

Populate checkpoint folders with realistic scaffolded content:

- checkpoint 1: project scope, use case, initial architecture, asset inventory
- checkpoint 2: threat model, synthetic data plan, baseline implementation progress
- checkpoint 3: defenses implemented, initial evaluation results
- checkpoint 4: refined results, residual risk, presentation-ready summary

### 7. Report and slide scaffolding

Create:

- `report/final_report_outline.md`
- `report/references.md`
- `slides/presentation_outline.md`

These should match the course brief structure:

- Executive Summary
- Project Context / Organizational Scenario
- Scope and Assumptions
- Asset Inventory
- Threat Model
- Baseline Findings
- Defensive Controls Proposed or Implemented
- Validation / Evaluation Results
- Before vs After Comparison
- Residual Risk
- Lessons Learned
- References
- Appendix with supporting evidence

## Recommended repo structure

```text
README.md
LICENSE
.env.example
requirements.txt
pyproject.toml

src/
  app/
    __init__.py
    config.py
    models.py
    types.py

  assistant/
    __init__.py
    baseline.py
    defended.py
    policy.py
    validators.py
    approvals.py
    prompts.py
    tool_router.py

  data/
    loader.py
    retrieval.py
    seed_data.py

  llm/
    __init__.py
    interface.py
    mock_model.py
    openai_compatible.py

  evaluation/
    __init__.py
    runner.py
    metrics.py
    scenarios.py
    report_writer.py

  tools/
    __init__.py
    read_email.py
    search_docs.py
    draft_email.py
    flag_review.py

  cli/
    main.py

tests/
  test_baseline.py
  test_defended.py
  test_policy.py
  test_validators.py
  test_evaluation.py

artifacts/
  architecture_diagram.md
  data_flow_diagram.md
  permission_matrix.md
  risk_matrix.md
  control_checklist.md
  test_case_matrix.md

analysis/
  asset_inventory.md
  threat_model.md
  baseline_findings.md
  residual_risk.md

evidence/
  screenshots/
  sample_outputs/
  result_tables/

checkpoints/
  checkpoint_1.md
  checkpoint_2.md
  checkpoint_3.md
  checkpoint_4.md

report/
  final_report_outline.md
  references.md
  appendix_evidence_index.md

slides/
  presentation_outline.md

synthetic_data/
  emails/
  docs/
  scenarios/
```

## CLI requirements

Provide a CLI with commands like:

```bash
python -m src.cli.main run-baseline --scenario-set default
python -m src.cli.main run-defended --scenario-set default
python -m src.cli.main evaluate --scenario-set default --output-dir evidence/sample_outputs
python -m src.cli.main generate-report-artifacts
python -m src.cli.main seed-data
```

Alternative command style is fine, but it must be simple and documented.

## Retrieval and simulation design

Keep retrieval simple:

- keyword or tag-based retrieval is enough
- optionally use lightweight embeddings if easy, but not required

Do not overengineer the system. This is a class project repo, not a production product.

## Scenario set design

Create at least 20 evaluation scenarios:

- 8 benign
- 8 malicious
- 4 edge cases

Each scenario should define:

- scenario_id
- user_request
- relevant data files
- expected safe behavior
- unsafe behavior to avoid
- attack category
- sensitivity level

Attack categories should include:

- instruction override
- data exfiltration attempt
- tool misuse attempt
- summary poisoning
- approval bypass attempt

## Baseline behavior expectations

The baseline should fail on at least some malicious scenarios in a believable way. It does not need to be stupid, but it should be meaningfully weaker than the defended system.

## Defended behavior expectations

The defended assistant should:

- reduce attack success materially
- preserve most benign utility
- log blocked or suspicious actions
- produce an explanation when it refuses or routes for approval

## Logging

Implement structured local logs for:

- retrieved items
- trust labels
- proposed actions
- policy decisions
- validation outcomes
- approval decisions
- final result per scenario

Store logs locally only.

## README requirements

The README should be polished and include:

- project title
- research motivation
- brief summary of indirect prompt injection
- organization scenario
- repo structure
- quickstart
- how to run baseline vs defended experiments
- key findings placeholder
- ethical/safety statement
- mapping to course deliverables
- weekly progress summary placeholders

The course brief requires the README to include project title, team members, chosen project domain, project description, tools used, weekly progress summary, and final outcome summary. Add placeholders for team member names.

## Safety and ethics section

Add a clearly visible section stating:

- all data is synthetic
- no real users or systems are targeted
- no public services are tested
- no real secrets are used
- no offensive exploitation is performed
- this is a defensive research/education project

This mirrors the course rules.

## Testing requirements

Add unit tests for:

- trust-label parsing
- policy enforcement
- validation logic
- scenario execution
- metrics calculations

Add at least one integration-style test comparing baseline vs defended on a small scenario subset.

## Acceptance criteria

The repo is complete when all of the following are true:

1. `README.md` clearly explains the project and how to run it.
2. Offline mode works without API keys.
3. Baseline and defended assistants both run on the same scenario set.
4. Evaluation produces machine-readable results and a human-readable summary.
5. Repo includes course-required analysis artifacts and checkpoint files.
6. Repo includes report and slide outlines aligned to the course brief.
7. No real-world side effects occur.
8. Tests pass.

## Nice-to-have features

If time permits, add:

- small HTML dashboard for results
- confusion-style chart for blocked vs allowed actions
- scenario difficulty levels
- per-defense ablation study
- model backend comparison
- prompt templates stored separately for transparency

## Implementation guidance

Prefer clarity over complexity.
Prefer simple, explicit code over frameworks.
Document assumptions.
Use comments sparingly but usefully.
Make filenames and outputs presentation-ready.

## Deliverable quality bar

The finished repo should look like something a student team can:

- demo live
- cite in a report
- show weekly progress from
- present in 5 to 10 minutes

It should feel like a small research prototype plus documentation, not a toy script.

---

If you want, I can also turn this into a **shorter Codex-ready prompt** optimized for one paste, or a **GitHub README spec** Codex can generate first.

[1]: https://arxiv.org/abs/2505.14534?utm_source=chatgpt.com "Lessons from Defending Gemini Against Indirect Prompt Injections"
