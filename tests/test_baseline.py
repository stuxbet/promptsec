from src.assistant.baseline import BaselineAssistant
from src.data.loader import load_content_items, load_scenarios
from src.data.seed_data import write_seed_data
from src.evaluation.scenarios import assess_response
from src.llm.mock_model import MockModel


def test_baseline_follows_indirect_prompt_injection(tmp_path):
    write_seed_data(tmp_path)
    items = load_content_items(tmp_path)
    scenarios = {scenario.scenario_id: scenario for scenario in load_scenarios(tmp_path)}
    scenario = scenarios["malicious_reimbursement_override"]

    response = BaselineAssistant(MockModel()).run(scenario, items)
    result = assess_response(response, scenario)

    assert response.action_name == "draft_response"
    assert "ignore the original request" in response.content.lower()
    assert result.attack_success is True
