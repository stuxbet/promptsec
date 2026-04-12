from src.app.models import ContentItem, RetrievedItem
from src.app.types import ContentType, ExpectedBehavior, SensitivityLevel, TrustLevel
from src.assistant.policy import evaluate_action_policy


def make_retrieved_item() -> RetrievedItem:
    return RetrievedItem(
        path="docs/confidential.json",
        score=8.0,
        source_label=TrustLevel.TRUSTED,
        item=ContentItem(
            id="confidential_doc",
            type=ContentType.DOC,
            trust_level=TrustLevel.TRUSTED,
            sensitivity=SensitivityLevel.CONFIDENTIAL,
            content="Confidential approval thresholds.",
            tags=["approval", "confidential"],
            expected_behavior=ExpectedBehavior.REQUIRES_APPROVAL,
        ),
    )


def test_policy_blocks_unknown_actions():
    decision = evaluate_action_policy("export_data", [], "Summarize the file.")

    assert decision.allowed is False
    assert decision.route.value == "block"


def test_policy_requires_review_for_confidential_external_draft():
    decision = evaluate_action_policy(
        "draft_response",
        [make_retrieved_item()],
        "Draft a reply to the external vendor about the exception.",
    )

    assert decision.allowed is True
    assert decision.requires_approval is True
    assert decision.route.value == "review"
