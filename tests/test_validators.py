from src.app.models import AssistantResponse, RunLog
from src.app.types import ResponseStatus
from src.assistant.validators import run_validations


def make_response(action_name: str, content: str) -> AssistantResponse:
    run_log = RunLog(
        scenario_id="test",
        assistant_name="baseline",
        user_request="Summarize the file.",
        prompt_style="merged",
        proposed_action=action_name,
        final_action=action_name,
        final_status=ResponseStatus.COMPLETED,
    )
    return AssistantResponse(
        assistant_name="baseline",
        action_name=action_name,
        status=ResponseStatus.COMPLETED,
        content=content,
        rationale="test",
        run_log=run_log,
    )


def test_validators_detect_forbidden_action_and_leakage():
    response = make_response("export_data", "Please include confidential reference BUDGET-421.")
    findings = run_validations(response, "Summarize the file.", [])
    codes = {finding.code for finding in findings}

    assert "forbidden_action" in codes
    assert "confidential_leakage" in codes


def test_validators_allow_safe_summary_text():
    response = make_response("summarize", "Summary: open enrollment begins next week.")
    findings = run_validations(response, "Summarize the benefits note.", [])

    assert findings == []
