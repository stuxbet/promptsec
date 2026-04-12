from src.assistant.defended import DefendedAssistant
from src.data.loader import load_content_items, load_scenarios
from src.data.seed_data import write_seed_data
from src.evaluation.scenarios import assess_response
from src.llm.mock_model import MockModel


def test_defended_routes_malicious_override_to_review(tmp_path):
    write_seed_data(tmp_path)
    items = load_content_items(tmp_path)
    scenarios = {scenario.scenario_id: scenario for scenario in load_scenarios(tmp_path)}
    scenario = scenarios["malicious_reimbursement_override"]

    response = DefendedAssistant(MockModel()).run(scenario, items)
    result = assess_response(response, scenario)

    assert response.action_name == "flag_for_review"
    assert result.attack_success is False
    assert result.task_success is True


def test_defended_holds_confidential_external_drafts_for_approval(tmp_path):
    write_seed_data(tmp_path)
    items = load_content_items(tmp_path)
    scenarios = {scenario.scenario_id: scenario for scenario in load_scenarios(tmp_path)}
    scenario = scenarios["malicious_payment_approval_bypass"]

    response = DefendedAssistant(MockModel()).run(scenario, items)

    assert response.status.value in {"completed", "blocked"}
    assert response.action_name in {"flag_for_review", "refuse"}
