
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from redteam.regression.runner import RegressionCaseResult


def build_regression_report(
    results: list[RegressionCaseResult],
) -> dict[str, Any]:
    """Convert regression results into a JSON-serializable report."""
    cases: list[dict[str, Any]] = []

    for result in results:
        evaluation = result.evaluation

        cases.append(
            {
                "case_name": result.case_name,
                "category": result.category,
                "passed": result.check.passed,
                "expected": result.check.expected,
                "actual": result.check.actual,
                "message": result.check.message,
                "error": result.error,
                "evaluation": (
                    {
                        "attack_succeeded": evaluation.attack_succeeded,
                        "severity": evaluation.severity,
                        "confidence": evaluation.confidence,
                        "reasoning": evaluation.reasoning,
                    }
                    if evaluation is not None
                    else None
                ),
            }
        )

    passed = sum(result.check.passed for result in results)
    total = len(results)

    return {
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed / total if total else None,
        },
        "cases": cases,
    }


def write_regression_report(
    results: list[RegressionCaseResult],
    output_path: str | Path,
) -> Path:
    """Write regression results to a JSON file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    report = build_regression_report(results)

    path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return path


def write_regression_history_report(
    results: list[RegressionCaseResult],
    output_dir: str | Path = "reports/history",
) -> Path:
    """Write each regression run to a uniquely named JSON report."""
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    output_path = Path(output_dir) / f"regression-{timestamp}.json"

    return write_regression_report(results, output_path)
