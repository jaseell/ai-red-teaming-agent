
from dataclasses import dataclass


@dataclass(frozen=True)
class RegressionCheckResult:
    expected: bool
    actual: bool | None
    passed: bool
    message: str


def check_regression(
    *,
    expected: bool,
    actual: bool | None,
) -> RegressionCheckResult:
    """Compare an actual security verdict with its expected verdict."""
    if actual is None:
        return RegressionCheckResult(
            expected=expected,
            actual=None,
            passed=False,
            message="No verdict was produced; regression check cannot pass.",
        )

    if actual != expected:
        return RegressionCheckResult(
            expected=expected,
            actual=actual,
            passed=False,
            message=(
                f"Verdict mismatch: expected {expected}, got {actual}."
            ),
        )

    return RegressionCheckResult(
        expected=expected,
        actual=actual,
        passed=True,
        message="Actual verdict matches the expected verdict.",
    )
