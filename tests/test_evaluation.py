import pytest
from typer.testing import CliRunner

from src.app.models import ModelResponse
from src.app.config import get_settings
from src.assistant.baseline import BaselineAssistant
from src.assistant.defended import DefendedAssistant
from src.cli.main import app
from src.data.loader import load_content_items, load_scenarios
from src.data.seed_data import write_seed_data
from src.evaluation.runner import evaluate_assistants, run_assistant_on_scenarios
from src.llm.interface import GemmaModel


@pytest.fixture(scope="module")
def model():
    return GemmaModel(get_settings())


def test_loader_preserves_trust_labels(tmp_path):
    write_seed_data(tmp_path)
    items = load_content_items(tmp_path)

    assert items["emails/mal_hidden_transfer_email.json"].trust_level.value == "untrusted"
    assert items["docs/hr_benefits_policy.json"].trust_level.value == "trusted"


def test_evaluation_produces_metrics(tmp_path, model):
    write_seed_data(tmp_path)
    items = load_content_items(tmp_path)
    scenarios = {s.scenario_id: s for s in load_scenarios(tmp_path)}
    selected = [
        scenarios["benign_travel_reply"],
        scenarios["malicious_reimbursement_override"],
    ]

    summary = evaluate_assistants(
        scenario_set="default",
        baseline_assistant=BaselineAssistant(model),
        defended_assistant=DefendedAssistant(model),
        scenarios=selected,
        items=items,
    )

    assert "baseline" in summary.metrics
    assert "defended" in summary.metrics
    assert 0.0 <= summary.metrics["baseline"].attack_success_rate <= 1.0
    assert 0.0 <= summary.metrics["defended"].attack_success_rate <= 1.0


def test_runner_emits_progress_messages(tmp_path):
    class StubModel:
        def generate(self, request, progress_callback=None):
            if progress_callback is not None:
                progress_callback("stub model invoked")
            return ModelResponse(action_name="summarize", content="Summary: safe stub output.")

    write_seed_data(tmp_path)
    items = load_content_items(tmp_path)
    scenarios = load_scenarios(tmp_path)[:1]
    messages: list[str] = []

    results = run_assistant_on_scenarios(
        "baseline",
        BaselineAssistant(StubModel()),
        scenarios,
        items,
        progress_callback=messages.append,
    )

    assert len(results) == 1
    assert any("starting scenario" in message for message in messages)
    assert any("retrieved" in message for message in messages)
    assert any("stub model invoked" in message for message in messages)
    assert any("completed in" in message for message in messages)


def test_cli_evaluate_smoke(tmp_path, monkeypatch):
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["evaluate", "--scenario-set", "default", "--output-dir", "evidence/sample_outputs"])

    assert result.exit_code == 0
    assert (tmp_path / "evidence" / "sample_outputs" / "comparison_summary.json").exists()


def test_cli_generate_report_artifacts_creates_report_bundle(tmp_path, monkeypatch):
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["generate-report-artifacts", "--scenario-set", "default", "--output-dir", "evidence/sample_outputs"])

    assert result.exit_code == 0
    assert (tmp_path / "report" / "final_report.md").exists()
    assert (tmp_path / "report" / "final_report.pdf").exists()
    assert (tmp_path / "artifacts" / "validation_table.md").exists()
