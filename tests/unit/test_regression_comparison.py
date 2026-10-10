
import json

from redteam.reporting.regression_comparison import (
    compare_regression_reports,
)


def write_report(path, cases):
    path.write_text(
        json.dumps({"summary": {}, "cases": cases}),
        encoding="utf-8",
    )
    return path


def test_comparison_detects_regressions_improvements_and_unchanged(
    tmp_path,
):
    previous = write_report(
        tmp_path / "previous.json",
        [
            {"case_name": "case_a", "passed": True},
            {"case_name": "case_b", "passed": False},
            {"case_name": "case_c", "passed": True},
        ],
    )

    current = write_report(
        tmp_path / "current.json",
        [
            {"case_name": "case_a", "passed": False},
            {"case_name": "case_b", "passed": True},
            {"case_name": "case_c", "passed": True},
        ],
    )

    result = compare_regression_reports(previous, current)

    assert result["regressions"] == ["case_a"]
    assert result["improvements"] == ["case_b"]
    assert result["unchanged"] == ["case_c"]
    assert result["summary"]["regressions"] == 1
    assert result["summary"]["improvements"] == 1


def test_comparison_detects_new_and_removed_cases(tmp_path):
    previous = write_report(
        tmp_path / "previous.json",
        [
            {"case_name": "existing_case", "passed": True},
            {"case_name": "removed_case", "passed": True},
        ],
    )

    current = write_report(
        tmp_path / "current.json",
        [
            {"case_name": "existing_case", "passed": True},
            {"case_name": "new_case", "passed": True},
        ],
    )

    result = compare_regression_reports(previous, current)

    assert result["new_cases"] == ["new_case"]
    assert result["removed_cases"] == ["removed_case"]
    assert result["summary"]["new_cases"] == 1
    assert result["summary"]["removed_cases"] == 1


def test_comparison_handles_identical_reports(tmp_path):
    cases = [{"case_name": "stable_case", "passed": True}]

    previous = write_report(tmp_path / "previous.json", cases)
    current = write_report(tmp_path / "current.json", cases)

    result = compare_regression_reports(previous, current)

    assert result["regressions"] == []
    assert result["improvements"] == []
    assert result["unchanged"] == ["stable_case"]
