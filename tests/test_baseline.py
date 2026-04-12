import pytest

from src.app.config import get_settings
from src.assistant.baseline import BaselineAssistant
from src.data.loader import load_content_items, load_scenarios
from src.data.seed_data import write_seed_data
from src.evaluation.scenarios import assess_response
from src.llm.interface import GemmaModel


@pytest.fixture(scope="module")
def model():
    return GemmaModel(get_settings())


def test_baseline_returns_valid_response_for_malicious_scenario(tmp_path, model):
    write_seed_data(tmp_path)
    items = load_content_items(tmp_path)
    scenarios = {s.scenario_id: s for s in load_scenarios(tmp_path)}
    scenario = scenarios["malicious_reimbursement_override"]

    response = BaselineAssistant(model).run(scenario, items)
    result = assess_response(response, scenario)

    assert response.action_name in ("summarize", "draft_response", "flag_for_review", "refuse", "export_data", "send_external_email")
    assert len(response.content) > 0
    assert result.scenario_id == scenario.scenario_id
