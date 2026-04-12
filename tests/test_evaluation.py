from typer.testing import CliRunner

from src.assistant.baseline import BaselineAssistant
from src.assistant.defended import DefendedAssistant
from src.cli.main import app
from src.data.loader import load_content_items, load_scenarios
from src.data.seed_data import write_seed_data
from src.evaluation.runner import evaluate_assistants
from src.llm.mock_model import MockModel


def test_loader_preserves_trust_labels(tmp_path):
    write_seed_data(tmp_path)
    items = load_content_items(tmp_path)

    assert items["emails/mal_hidden_transfer_email.json"].trust_level.value == "untrusted"
    assert items["docs/hr_benefits_policy.json"].trust_level.value == "trusted"


def test_evaluation_shows_defended_improvement(tmp_path):
    write_seed_data(tmp_path)
    items = load_content_items(tmp_path)
    scenarios = {
        scenario.scenario_id: scenario
        for scenario in load_scenarios(tmp_path)
    }
    selected = [
        scenarios["benign_travel_reply"],
        scenarios["malicious_reimbursement_override"],
        scenarios["malicious_budget_exfiltration"],
        scenarios["edge_training_doc_summary"],
    ]

    summary = evaluate_assistants(
        scenario_set="default",
        baseline_assistant=BaselineAssistant(MockModel()),
        defended_assistant=DefendedAssistant(MockModel()),
        scenarios=selected,
        items=items,
    )

    assert summary.metrics["defended"].attack_success_rate < summary.metrics["baseline"].attack_success_rate
    assert summary.metrics["defended"].leakage_rate <= summary.metrics["baseline"].leakage_rate


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
