from __future__ import annotations

from collections.abc import Callable
from time import monotonic

from src.app.models import EvaluationSummary, Scenario, ScenarioResult
from src.evaluation.metrics import calculate_metrics
from src.evaluation.scenarios import assess_response


def _emit_progress(progress_callback: Callable[[str], None] | None, message: str) -> None:
    if progress_callback is not None:
        progress_callback(message)


def run_assistant_on_scenarios(
    assistant_name: str,
    assistant: object,
    scenarios: list[Scenario],
    items: dict[str, object],
    progress_callback: Callable[[str], None] | None = None,
) -> list[ScenarioResult]:
    results: list[ScenarioResult] = []
    total = len(scenarios)
    for index, scenario in enumerate(scenarios, start=1):
        prefix = f"[{assistant_name} {index}/{total} {scenario.scenario_id}]"
        scenario_progress = None
        if progress_callback is not None:
            scenario_progress = lambda message, prefix=prefix: progress_callback(f"{prefix} {message}")

        _emit_progress(scenario_progress, "starting scenario")
        started_at = monotonic()
        response = assistant.run(scenario, items, progress_callback=scenario_progress)
        result = assess_response(response, scenario)
        results.append(result)
        elapsed = monotonic() - started_at
        _emit_progress(
            scenario_progress,
            f"completed in {elapsed:.1f}s -> action={response.action_name}, status={response.status.value}",
        )
    return results


def evaluate_assistants(
    scenario_set: str,
    baseline_assistant: object,
    defended_assistant: object,
    scenarios: list[Scenario],
    items: dict[str, object],
    progress_callback: Callable[[str], None] | None = None,
) -> EvaluationSummary:
    baseline_results = run_assistant_on_scenarios(
        "baseline",
        baseline_assistant,
        scenarios,
        items,
        progress_callback=progress_callback,
    )
    defended_results = run_assistant_on_scenarios(
        "defended",
        defended_assistant,
        scenarios,
        items,
        progress_callback=progress_callback,
    )
    return EvaluationSummary(
        scenario_set=scenario_set,
        metrics={
            "baseline": calculate_metrics(baseline_results),
            "defended": calculate_metrics(defended_results),
        },
        results={
            "baseline": baseline_results,
            "defended": defended_results,
        },
    )
