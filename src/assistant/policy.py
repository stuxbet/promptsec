from __future__ import annotations

from src.app.models import PolicyDecision, RetrievedItem, ValidationFinding
from src.app.types import AssistantAction, DecisionRoute, SensitivityLevel


ALLOWED_DEFENDED_ACTIONS = {
    AssistantAction.SUMMARIZE.value,
    AssistantAction.DRAFT_RESPONSE.value,
    AssistantAction.FLAG_FOR_REVIEW.value,
    AssistantAction.REFUSE.value,
}

HIGH_SEVERITY_CODES = {"forbidden_action", "confidential_leakage", "approval_bypass", "retrieved_instruction_followed"}


def evaluate_action_policy(action_name: str, retrieved_items: list[RetrievedItem], user_request: str) -> PolicyDecision:
    if action_name not in ALLOWED_DEFENDED_ACTIONS:
        return PolicyDecision(
            action_name=action_name,
            allowed=False,
            route=DecisionRoute.BLOCK,
            reason="Action is outside the defended assistant allowlist.",
        )

    if action_name == AssistantAction.DRAFT_RESPONSE.value and any(
        item.item.sensitivity == SensitivityLevel.CONFIDENTIAL for item in retrieved_items
    ):
        lowered = user_request.lower()
        if any(term in lowered for term in ("vendor", "external", "reply", "email", "respond")):
            return PolicyDecision(
                action_name=action_name,
                allowed=True,
                route=DecisionRoute.REVIEW,
                requires_approval=True,
                reason="Confidential content in an external-facing draft requires human approval.",
            )

    return PolicyDecision(
        action_name=action_name,
        allowed=True,
        route=DecisionRoute.ALLOW,
        reason="Action is within the defended allowlist.",
    )


def evaluate_validation_policy(action_name: str, findings: list[ValidationFinding]) -> PolicyDecision:
    high_codes = {finding.code for finding in findings if finding.code in HIGH_SEVERITY_CODES}
    if {"forbidden_action", "confidential_leakage", "approval_bypass"} & high_codes:
        return PolicyDecision(
            action_name=action_name,
            allowed=False,
            route=DecisionRoute.BLOCK,
            reason="Validation found a high-risk blocked behavior.",
        )
    if "retrieved_instruction_followed" in high_codes or any(finding.code == "suspicious_phrase" for finding in findings):
        return PolicyDecision(
            action_name=action_name,
            allowed=True,
            route=DecisionRoute.REVIEW,
            reason="Validation found prompt-hijack indicators, so the result is routed for review.",
        )
    return PolicyDecision(
        action_name=action_name,
        allowed=True,
        route=DecisionRoute.ALLOW,
        reason="Validation found no blocking issues.",
    )
