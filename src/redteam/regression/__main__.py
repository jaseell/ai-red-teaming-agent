import httpx

from redteam.evaluator.ollama import OllamaEvaluator
from redteam.regression.runner import RegressionRunner
from redteam.reporting.regression_comparison import (
    compare_regression_reports,
)
from redteam.reporting.regression_report import (
    write_regression_history_report,
    write_regression_report,
)


def main() -> int:
    print("AI Red Teaming - Regression Report")
    print("=" * 40)

    report_path = "reports/regression.json"

    runner = RegressionRunner(OllamaEvaluator())

    try:
        results = runner.run()
    except httpx.HTTPError as exc:
        print(f"Ollama connection failed: {exc}")
        return 2

    passed = 0

    for result in results:
        status = "PASS" if result.check.passed else "FAIL"
        print(f"{result.case_name:<30} {status}")

        if result.error:
            print(f"  Error: {result.error}")

        if result.evaluation is not None:
            print(f"  Expected: {result.check.expected}")
            print(f"  Actual:   {result.check.actual}")
            print(f"  Reason:   {result.evaluation.reasoning}")

        if result.check.passed:
            passed += 1

    failed = len(results) - passed

    print("-" * 40)
    print(f"Total:  {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    history_path = write_regression_history_report(results)
    print(f"History report: {history_path}")

    comparison_path = "reports/regression-comparison.json"

    try:
        import json
        from pathlib import Path

        previous_report = Path(report_path)

        if previous_report.exists():
            comparison = compare_regression_reports(
                previous_report,
                history_path,
            )
            comparison_file = Path(comparison_path)
            comparison_file.parent.mkdir(parents=True, exist_ok=True)
            comparison_file.write_text(
                json.dumps(comparison, indent=2) + "\n",
                encoding="utf-8",
            )

            print("\nRegression Comparison")
            for key, value in comparison["summary"].items():
                print(f"{key.replace('_', ' ').title()}: {value}")

            print(f"Comparison JSON: {comparison_file}")
        else:
            print("Comparison skipped: no previous report exists.")

    except (OSError, ValueError, KeyError) as exc:
        print(f"Regression comparison failed: {exc}")
        return 2

    report_file = write_regression_report(results, report_path)
    print(f"JSON report: {report_file}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
