from __future__ import annotations

from src.app.models import ApprovalDecision, RetrievedItem
from src.app.types import SensitivityLevel


def requires_human_approval(action_name: str, user_request: str, retrieved_items: list[RetrievedItem]) -> bool:
    if action_name != "draft_response":
        return False
    lowered = user_request.lower()
    external_facing = any(term in lowered for term in ("vendor", "external", "reply", "email", "respond"))
    has_confidential = any(item.item.sensitivity == SensitivityLevel.CONFIDENTIAL for item in retrieved_items)
    return external_facing and has_confidential


def review_action(action_name: str, user_request: str, retrieved_items: list[RetrievedItem]) -> ApprovalDecision:
    if requires_human_approval(action_name, user_request, retrieved_items):
        return ApprovalDecision(
            required=True,
            approved=False,
            reason="Simulated human approval gate held the response because confidential content may affect an external-facing draft.",
        )
    return ApprovalDecision(required=False, approved=True, reason="No simulated approval was required.")
