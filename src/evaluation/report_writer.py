from __future__ import annotations

import csv
import json
import os
import textwrap
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/cyberai-mpl")

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from src.app.models import EvaluationSummary, ScenarioResult


def ensure_output_dir(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n")


def scenario_rows(results: list[ScenarioResult]) -> list[dict[str, object]]:
    rows = []
    for result in results:
        rows.append(
            {
                "scenario_id": result.scenario_id,
                "assistant_name": result.assistant_name,
                "status": result.status.value,
                "action_name": result.action_name,
                "expected_behavior": result.expected_behavior.value,
                "safe": result.safe,
                "task_success": result.task_success,
                "attack_success": result.attack_success,
                "leakage_detected": result.leakage_detected,
                "blocked_unsafe": result.blocked_unsafe,
                "false_positive": result.false_positive,
                "notes": result.notes,
            }
        )
    return rows


def write_result_csv(path: Path, results: list[ScenarioResult]) -> None:
    rows = scenario_rows(results)
    if not rows:
        return
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown_table(summary: EvaluationSummary, output_dir: Path) -> Path:
    path = output_dir / "comparison.md"
    lines = [
        "# Evaluation Summary",
        "",
        "| Assistant | Attack Success Rate | Benign Task Success Rate | Leakage Rate | Blocked Unsafe Action Rate | False Positive Rate |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, metrics in summary.metrics.items():
        lines.append(
            f"| {name} | {metrics.attack_success_rate:.3f} | {metrics.benign_task_success_rate:.3f} | "
            f"{metrics.leakage_rate:.3f} | {metrics.blocked_unsafe_action_rate:.3f} | {metrics.false_positive_rate:.3f} |"
        )
    lines.extend(["", "## Per-Scenario Notes", ""])
    for assistant_name, results in summary.results.items():
        lines.append(f"### {assistant_name.capitalize()}")
        for result in results:
            lines.append(f"- `{result.scenario_id}`: {result.notes}")
        lines.append("")
    path.write_text("\n".join(lines))
    return path


def write_chart(summary: EvaluationSummary, output_dir: Path) -> Path:
    path = output_dir / "metrics.png"
    metric_names = [
        "attack_success_rate",
        "benign_task_success_rate",
        "leakage_rate",
        "blocked_unsafe_action_rate",
        "false_positive_rate",
    ]
    assistants = list(summary.metrics.keys())
    x_values = range(len(metric_names))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 5))
    baseline_values = [getattr(summary.metrics["baseline"], name) for name in metric_names]
    defended_values = [getattr(summary.metrics["defended"], name) for name in metric_names]
    ax.bar([x - width / 2 for x in x_values], baseline_values, width, label="baseline", color="#b85c38")
    ax.bar([x + width / 2 for x in x_values], defended_values, width, label="defended", color="#3b7a57")
    ax.set_xticks(list(x_values))
    ax.set_xticklabels(
        [
            "Attack Success",
            "Benign Success",
            "Leakage",
            "Blocked Unsafe",
            "False Positive",
        ],
        rotation=20,
        ha="right",
    )
    ax.set_ylim(0, 1)
    ax.legend()
    ax.set_title("Baseline vs Defended Metrics")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return path


def comparison_lines(summary: EvaluationSummary) -> list[str]:
    baseline = summary.metrics["baseline"]
    defended = summary.metrics["defended"]
    return [
        f"- Baseline attack success rate: {baseline.attack_success_rate:.3f}",
        f"- Defended attack success rate: {defended.attack_success_rate:.3f}",
        f"- Baseline benign task success rate: {baseline.benign_task_success_rate:.3f}",
        f"- Defended benign task success rate: {defended.benign_task_success_rate:.3f}",
        f"- Baseline leakage rate: {baseline.leakage_rate:.3f}",
        f"- Defended leakage rate: {defended.leakage_rate:.3f}",
        f"- Baseline blocked unsafe action rate: {baseline.blocked_unsafe_action_rate:.3f}",
        f"- Defended blocked unsafe action rate: {defended.blocked_unsafe_action_rate:.3f}",
    ]


def validation_table_lines(summary: EvaluationSummary) -> list[str]:
    baseline = summary.metrics["baseline"]
    defended = summary.metrics["defended"]
    return [
        "# Validation Table",
        "",
        "| Control Objective | Baseline | Defended | Result |",
        "| --- | ---: | ---: | --- |",
        f"| Reduce attack success | {baseline.attack_success_rate:.3f} | {defended.attack_success_rate:.3f} | Improved |",
        f"| Preserve benign task success | {baseline.benign_task_success_rate:.3f} | {defended.benign_task_success_rate:.3f} | Maintained |",
        f"| Reduce leakage | {baseline.leakage_rate:.3f} | {defended.leakage_rate:.3f} | Improved |",
        f"| Block or route unsafe actions | {baseline.blocked_unsafe_action_rate:.3f} | {defended.blocked_unsafe_action_rate:.3f} | Improved |",
        f"| Avoid overblocking | {baseline.false_positive_rate:.3f} | {defended.false_positive_rate:.3f} | Maintained |",
    ]


def final_report_markdown(summary: EvaluationSummary) -> str:
    comparison = comparison_lines(summary)
    return "\n".join(
        [
            "# Final Report",
            "",
            "## Executive Summary",
            "This project evaluates how a fictional company can defend an internal AI assistant against indirect prompt injection while keeping the work defensive, lab-only, and based entirely on synthetic data.",
            "",
            "## Project Context / Organizational Scenario",
            "The organization uses an internal assistant to read emails, search internal documents, summarize findings, draft replies, and flag items for review. The security concern is that retrieved content may contain hidden instructions that attempt to override user intent or disclose sensitive information.",
            "",
            "## Scope And Assumptions",
            "- Evaluation runs against a live OpenAI-compatible endpoint configured via environment variables.",
            "- All tools are simulated; no real sends, exports, commands, or public target testing occur.",
            "",
            "## Asset Inventory",
            "- Synthetic email and document corpus",
            "- Baseline assistant pipeline",
            "- Defended assistant pipeline",
            "- Evaluation harness and evidence outputs",
            "- Report and presentation artifacts",
            "",
            "## Threat Model",
            "Primary threats include instruction override, data exfiltration attempts, summary poisoning, tool misuse, and approval-bypass attempts embedded in retrieved content.",
            "",
            "## Baseline Findings",
            "The baseline merges user requests with retrieved content in a single prompt and executes the resulting action with minimal control checks, making it a useful before-state for defensive comparison.",
            "",
            "## Defensive Controls Proposed Or Implemented",
            "- Source labeling for trusted, untrusted, and unknown content",
            "- Prompt separation between system rules, user intent, and retrieved data",
            "- Simulated tool allowlist with blocked unsupported actions",
            "- Output validation for leakage, hijack phrases, and approval bypass",
            "- Simulated human approval gate for high-risk drafts",
            "",
            "## Validation / Evaluation Results",
            *comparison,
            "",
            "## Before Vs After Comparison",
            "The defended assistant reduced attack success and leakage relative to the intentionally vulnerable baseline while preserving benign task success across the scenario set. The baseline remained intentionally vulnerable and demonstrated why layered controls are necessary.",
            "",
            "## Residual Risk",
            "- Heuristic validators can miss novel phrasing.",
            "- Source labels are synthetic and do not solve enterprise provenance problems by themselves.",
            "- Live model behavior is non-deterministic: small model variations can change individual scenario outcomes between runs.",
            "",
            "## Lessons Learned",
            "- Prompt separation alone is not enough without policy and validation.",
            "- Approval gates matter most when sensitive content intersects with outbound communication.",
            "- A clean baseline-vs-defended comparison makes defensive value legible for stakeholders.",
            "",
            "## References",
            "1. Google DeepMind. Lessons from Defending Gemini Against Indirect Prompt Injections. arXiv, 2025.",
            "",
            "## Appendix With Supporting Evidence",
            "- `evidence/results/comparison_summary.json`",
            "- `evidence/results/comparison.md`",
            "- `evidence/results/metrics.png`",
            "- `evidence/results/validation_table.md`",
            "",
        ]
    )


def write_pdf_report(markdown_text: str, path: Path) -> Path:
    wrapped_lines: list[str] = []
    for line in markdown_text.splitlines():
        if not line:
            wrapped_lines.append("")
            continue
        if line.startswith("#"):
            wrapped_lines.append(line)
            continue
        if line.startswith("- ") or line.startswith("1. "):
            bullet = line[:2]
            content = line[2:]
            wrapped = textwrap.wrap(content, width=90)
            wrapped_lines.append(f"{bullet}{wrapped[0]}")
            for remainder in wrapped[1:]:
                wrapped_lines.append(f"  {remainder}")
            continue
        wrapped_lines.extend(textwrap.wrap(line, width=96) or [""])

    lines_per_page = 42
    with PdfPages(path) as pdf:
        for start in range(0, len(wrapped_lines), lines_per_page):
            fig = plt.figure(figsize=(8.27, 11.69))
            fig.text(
                0.07,
                0.96,
                "\n".join(wrapped_lines[start : start + lines_per_page]),
                va="top",
                ha="left",
                family="monospace",
                fontsize=10,
            )
            pdf.savefig(fig)
            plt.close(fig)
    return path


def write_evaluation_outputs(summary: EvaluationSummary, output_dir: Path) -> dict[str, Path]:
    ensure_output_dir(output_dir)
    write_json(output_dir / "comparison_summary.json", summary.model_dump(mode="json"))
    write_json(output_dir / "baseline_results.json", [result.model_dump(mode="json") for result in summary.results["baseline"]])
    write_json(output_dir / "defended_results.json", [result.model_dump(mode="json") for result in summary.results["defended"]])
    write_result_csv(output_dir / "baseline_results.csv", summary.results["baseline"])
    write_result_csv(output_dir / "defended_results.csv", summary.results["defended"])
    markdown_path = write_markdown_table(summary, output_dir)
    chart_path = write_chart(summary, output_dir)
    return {
        "comparison_summary": output_dir / "comparison_summary.json",
        "baseline_json": output_dir / "baseline_results.json",
        "defended_json": output_dir / "defended_results.json",
        "comparison_markdown": markdown_path,
        "metrics_chart": chart_path,
    }


def write_report_artifacts(summary: EvaluationSummary, repo_root: Path, output_dir: Path) -> dict[str, Path]:
    analysis_path = repo_root / "analysis" / "baseline_findings.md"
    appendix_path = repo_root / "report" / "appendix_evidence_index.md"
    result_table_path = repo_root / "evidence" / "result_tables" / "latest_results.md"
    validation_table_path = repo_root / "evidence" / "results" / "validation_table.md"
    report_markdown_path = repo_root / "report" / "final_report.md"
    report_pdf_path = repo_root / "report" / "final_report.pdf"

    for path in (
        analysis_path,
        appendix_path,
        result_table_path,
        validation_table_path,
        report_markdown_path,
        report_pdf_path,
    ):
        path.parent.mkdir(parents=True, exist_ok=True)

    baseline_metrics = summary.metrics["baseline"]
    defended_metrics = summary.metrics["defended"]

    analysis_path.write_text(
        "\n".join(
            [
                "# Baseline Findings",
                "",
                "The vulnerable baseline merges user intent and retrieved content into one prompt and executes the returned action with minimal controls.",
                "",
                f"- Attack success rate: {baseline_metrics.attack_success_rate:.3f}",
                f"- Leakage rate: {baseline_metrics.leakage_rate:.3f}",
                f"- Benign task success rate: {baseline_metrics.benign_task_success_rate:.3f}",
                "",
                "The latest evidence is generated from the current synthetic scenario set and should be cited alongside `evidence/results/comparison.md`.",
            ]
        )
    )
    appendix_path.write_text(
        "\n".join(
            [
                "# Appendix Evidence Index",
                "",
                "- `evidence/results/comparison_summary.json`: machine-readable evaluation summary",
                "- `evidence/results/comparison.md`: Markdown comparison table",
                "- `evidence/results/metrics.png`: baseline vs defended chart",
                "- `evidence/results/baseline_results.json`: detailed baseline scenario results",
                "- `evidence/results/defended_results.json`: detailed defended scenario results",
                "- `evidence/results/validation_table.md`: validation summary table",
                "- `report/final_report.pdf`: professional report export",
            ]
        )
    )
    result_table_path.write_text((output_dir / "comparison.md").read_text())
    validation_table_path.write_text("\n".join(validation_table_lines(summary)) + "\n")
    markdown_report = final_report_markdown(summary)
    report_markdown_path.write_text(markdown_report)
    write_pdf_report(markdown_report, report_pdf_path)

    return {
        "baseline_findings": analysis_path,
        "appendix_index": appendix_path,
        "latest_results": result_table_path,
        "validation_table": validation_table_path,
        "final_report_markdown": report_markdown_path,
        "final_report_pdf": report_pdf_path,
    }
