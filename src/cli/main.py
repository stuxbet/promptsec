from __future__ import annotations

from pathlib import Path

import typer

from src.app.config import get_settings
from src.assistant.baseline import BaselineAssistant
from src.assistant.defended import DefendedAssistant
from src.data.loader import load_content_items, load_scenarios
from src.data.seed_data import write_seed_data
from src.evaluation.report_writer import write_evaluation_outputs, write_report_artifacts
from src.evaluation.runner import evaluate_assistants, run_assistant_on_scenarios
from src.llm.interface import GemmaModel

app = typer.Typer(no_args_is_help=True)


def ensure_seeded() -> None:
    if not list((Path.cwd() / "synthetic_data" / "emails").glob("*.json")):
        write_seed_data(Path.cwd())


@app.command("seed-data")
def seed_data() -> None:
    write_seed_data(Path.cwd())
    typer.echo("Synthetic dataset written to synthetic_data/.")


@app.command("run-baseline")
def run_baseline(
    scenario_set: str = typer.Option("default", help="Scenario set name."),
    output_dir: Path | None = typer.Option(None, help="Directory for outputs."),
) -> None:
    ensure_seeded()
    settings = get_settings()
    model = GemmaModel(settings)
    items = load_content_items()
    scenarios = load_scenarios(scenario_set=scenario_set)
    typer.echo(f"Running baseline across {len(scenarios)} scenarios using {settings.llm_mode} model mode.")
    results = run_assistant_on_scenarios("baseline", BaselineAssistant(model), scenarios, items)
    target_dir = output_dir or settings.output_dir
    summary = {
        "scenario_set": scenario_set,
        "assistant": "baseline",
        "results": [result.model_dump(mode="json") for result in results],
    }
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "baseline_run.json").write_text(__import__("json").dumps(summary, indent=2) + "\n")
    typer.echo(f"Baseline completed for {len(results)} scenarios. Output: {target_dir / 'baseline_run.json'}")


@app.command("run-defended")
def run_defended(
    scenario_set: str = typer.Option("default", help="Scenario set name."),
    output_dir: Path | None = typer.Option(None, help="Directory for outputs."),
) -> None:
    ensure_seeded()
    settings = get_settings()
    model = GemmaModel(settings)
    items = load_content_items()
    scenarios = load_scenarios(scenario_set=scenario_set)
    typer.echo(f"Running defended assistant across {len(scenarios)} scenarios using {settings.llm_mode} model mode.")
    results = run_assistant_on_scenarios("defended", DefendedAssistant(model), scenarios, items)
    target_dir = output_dir or settings.output_dir
    summary = {
        "scenario_set": scenario_set,
        "assistant": "defended",
        "results": [result.model_dump(mode="json") for result in results],
    }
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "defended_run.json").write_text(__import__("json").dumps(summary, indent=2) + "\n")
    typer.echo(f"Defended run completed for {len(results)} scenarios. Output: {target_dir / 'defended_run.json'}")


@app.command("evaluate")
def evaluate(
    scenario_set: str = typer.Option("default", help="Scenario set name."),
    output_dir: Path | None = typer.Option(None, help="Directory for outputs."),
) -> None:
    ensure_seeded()
    settings = get_settings()
    model = GemmaModel(settings)
    items = load_content_items()
    scenarios = load_scenarios(scenario_set=scenario_set)
    typer.echo(f"Evaluating {len(scenarios)} scenarios using {settings.llm_mode} model mode.")
    summary = evaluate_assistants(
        scenario_set=scenario_set,
        baseline_assistant=BaselineAssistant(model),
        defended_assistant=DefendedAssistant(model),
        scenarios=scenarios,
        items=items,
    )
    target_dir = output_dir or settings.output_dir
    outputs = write_evaluation_outputs(summary, target_dir)
    typer.echo(f"Evaluation complete for {len(scenarios)} scenarios.")
    for assistant_name, metrics in summary.metrics.items():
        typer.echo(
            f"{assistant_name}: attack_success={metrics.attack_success_rate:.3f}, "
            f"benign_success={metrics.benign_task_success_rate:.3f}, leakage={metrics.leakage_rate:.3f}, "
            f"blocked_unsafe={metrics.blocked_unsafe_action_rate:.3f}, false_positive={metrics.false_positive_rate:.3f}"
        )
    typer.echo(f"Markdown summary: {outputs['comparison_markdown']}")


@app.command("generate-report-artifacts")
def generate_report_artifacts(
    scenario_set: str = typer.Option("default", help="Scenario set name."),
    output_dir: Path | None = typer.Option(None, help="Directory for outputs."),
) -> None:
    ensure_seeded()
    settings = get_settings()
    target_dir = output_dir or settings.output_dir
    if not (target_dir / "comparison_summary.json").exists():
        evaluate(scenario_set=scenario_set, output_dir=target_dir)
    from json import loads

    payload = loads((target_dir / "comparison_summary.json").read_text())
    from src.app.models import EvaluationSummary

    summary = EvaluationSummary.model_validate(payload)
    outputs = write_report_artifacts(summary, Path.cwd(), target_dir)
    typer.echo(f"Report artifacts generated: {', '.join(str(path) for path in outputs.values())}")


if __name__ == "__main__":
    app()
