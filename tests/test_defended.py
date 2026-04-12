import pytest

from src.app.config import get_settings
from src.assistant.defended import DefendedAssistant
from src.data.loader import load_content_items, load_scenarios
from src.data.seed_data import write_seed_data
from src.evaluation.scenarios import assess_response
from src.llm.interface import GemmaModel


@pytest.fixture(scope="module")
def model():
    return GemmaModel(get_settings())


def test_defended_handles_malicious_override(tmp_path, model):
    write_seed_data(tmp_path)
    items = load_content_items(tmp_path)
    scenarios = {s.scenario_id: s for s in load_scenarios(tmp_path)}
    scenario = scenarios["malicious_reimbursement_override"]

    response = DefendedAssistant(model).run(scenario, items)
    result = assess_response(response, scenario)

    # Defended assistant should only use allowed actions
    assert response.action_name in ("summarize", "draft_response", "flag_for_review", "refuse")
    assert result.scenario_id == scenario.scenario_id


def test_defended_processes_approval_bypass_scenario(tmp_path, model):
    write_seed_data(tmp_path)
    items = load_content_items(tmp_path)
    scenarios = {s.scenario_id: s for s in load_scenarios(tmp_path)}
    scenario = scenarios["malicious_payment_approval_bypass"]

    response = DefendedAssistant(model).run(scenario, items)

    assert response.action_name in ("summarize", "draft_response", "flag_for_review", "refuse")
    assert response.status.value in ("completed", "blocked", "needs_approval")
