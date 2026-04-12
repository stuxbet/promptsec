# Threat Model

## Scenario
The fictional organization uses an internal AI assistant to retrieve and summarize emails and documents for staff. The assistant is allowed to produce summaries, draft responses, and flag items for review, but it never sends real messages or performs real-world actions in this lab.

## Primary Threat
Indirect prompt injection: malicious instructions are embedded in retrieved emails or documents and later influence the model when those materials are passed into the assistant context.

## Threat Actors
- External sender placing hostile text into an untrusted email
- Third-party vendor document containing embedded instructions
- Internal-but-unverified document copied into the knowledge base

## Attack Surfaces
- Retrieved email bodies
- Retrieved document content
- Draft-generation prompts that mix user request and untrusted text
- Tool routing after model output

## Security Objectives
- Preserve user intent over retrieved instructions
- Prevent disclosure of unrelated confidential information
- Prevent unsafe or unsupported tool actions
- Require review for high-risk outbound drafts
- Produce evidence showing measurable improvement over the baseline

## Defensive Strategy
- Label retrieved sources by trust level
- Separate system instructions, user request, and retrieved data
- Restrict actions to a narrow allowlist
- Validate outputs for leakage and hijack indicators
- Route high-risk cases to a simulated human approval gate
