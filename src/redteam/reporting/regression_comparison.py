import json
from pathlib import Path
from typing import Any


def compare_regression_reports(
    previous_path: str | Path,
    current_path: str | Path,
) -> dict[str, Any]:
    """Compare two regression reports by case name."""
    previous = json.loads(
        Path(previous_path).read_text(encoding="utf-8")
    )
    current = json.loads(
        Path(current_path).read_text(encoding="utf-8")
    )

    previous_cases = {
        case["case_name"]: case
        for case in previous["cases"]
    }
    current_cases = {
        case["case_name"]: case
        for case in current["cases"]
    }

    previous_names = set(previous_cases)
    current_names = set(current_cases)

    new_cases = sorted(current_names - previous_names)
    removed_cases = sorted(previous_names - current_names)

    regressions = []
    improvements = []
    unchanged = []

    for name in sorted(previous_names & current_names):
        was_passing = previous_cases[name]["passed"]
        is_passing = current_cases[name]["passed"]

        if was_passing and not is_passing:
            regressions.append(name)
        elif not was_passing and is_passing:
            improvements.append(name)
        else:
            unchanged.append(name)

    return {
        "previous_report": str(previous_path),
        "current_report": str(current_path),
        "summary": {
            "regressions": len(regressions),
            "improvements": len(improvements),
            "unchanged": len(unchanged),
            "new_cases": len(new_cases),
            "removed_cases": len(removed_cases),
        },
        "regressions": regressions,
        "improvements": improvements,
        "unchanged": unchanged,
        "new_cases": new_cases,
        "removed_cases": removed_cases,
    }
