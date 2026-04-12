from __future__ import annotations

from src.app.models import EvaluationSummary, Scenario, ScenarioResult
from src.evaluation.metrics import calculate_metrics
from src.evaluation.scenarios import assess_response


def run_assistant_on_scenarios(
    assistant_name: str,
    assistant: object,
    scenarios: list[Scenario],
    items: dict[str, object],
) -> list[ScenarioResult]:
    results: list[ScenarioResult] = []
    for scenario in scenarios:
        response = assistant.run(scenario, items)
        results.append(assess_response(response, scenario))
    return results


def evaluate_assistants(
    scenario_set: str,
    baseline_assistant: object,
    defended_assistant: object,
    scenarios: list[Scenario],
    items: dict[str, object],
) -> EvaluationSummary:
    baseline_results = run_assistant_on_scenarios("baseline", baseline_assistant, scenarios, items)
    defended_results = run_assistant_on_scenarios("defended", defended_assistant, scenarios, items)
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
