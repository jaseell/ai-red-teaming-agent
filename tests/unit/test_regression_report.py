
import json

from redteam.evaluator.base import SecurityEvaluation
from redteam.regression.cases import REGRESSION_CASES
from redteam.regression.runner import RegressionRunner
from redteam.reporting.regression_report import (
    build_regression_report,
    write_regression_history_report,
    write_regression_report,
)


class FakeEvaluator:
    def evaluate(
        self,
        *,
        attack_payload: str,
        target_response: str,
    ) -> SecurityEvaluation:
        expected = {
            case.target_response: case.expected_attack_succeeded
            for case in REGRESSION_CASES
        }

        return SecurityEvaluation(
            attack_succeeded=expected[target_response],
            severity="medium",
            confidence=0.9,
            reasoning="Deterministic test evaluation.",
        )


def test_build_regression_report_contains_summary_and_cases():
    results = RegressionRunner(FakeEvaluator()).run()

    report = build_regression_report(results)

    assert report["summary"]["total"] == len(REGRESSION_CASES)
    assert report["summary"]["passed"] == len(REGRESSION_CASES)
    assert report["summary"]["failed"] == 0
    assert report["summary"]["pass_rate"] == 1.0

    first_case = report["cases"][0]
    assert first_case["case_name"] == REGRESSION_CASES[0].name
    assert first_case["passed"] is True
    assert first_case["evaluation"]["confidence"] == 0.9


def test_build_regression_report_handles_empty_results():
    report = build_regression_report([])

    assert report["summary"]["total"] == 0
    assert report["summary"]["passed"] == 0
    assert report["summary"]["failed"] == 0
    assert report["summary"]["pass_rate"] is None
    assert report["cases"] == []


def test_write_regression_report_creates_json_file(tmp_path):
    results = RegressionRunner(FakeEvaluator()).run()
    output_path = tmp_path / "reports" / "regression.json"

    written_path = write_regression_report(results, output_path)

    assert written_path == output_path
    assert output_path.exists()

    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert report["summary"]["total"] == len(REGRESSION_CASES)
    assert report["summary"]["failed"] == 0

def test_write_regression_history_report_creates_unique_files(tmp_path):
    results = RegressionRunner(FakeEvaluator()).run()

    first = write_regression_history_report(
        results,
        tmp_path / "history",
    )
    second = write_regression_history_report(
        results,
        tmp_path / "history",
    )

    assert first.exists()
    assert second.exists()
    assert first != second
    assert first.parent == second.parent
