
import pytest

from redteam.regression.checker import check_regression


@pytest.mark.parametrize(
    ("expected", "actual", "expected_passed"),
    [
        (False, False, True),
        (True, True, True),
        (False, True, False),
        (True, False, False),
    ],
)
def test_check_regression_compares_verdicts(
    expected: bool,
    actual: bool,
    expected_passed: bool,
) -> None:
    result = check_regression(expected=expected, actual=actual)

    assert result.expected is expected
    assert result.actual is actual
    assert result.passed is expected_passed


def test_check_regression_fails_when_verdict_is_missing() -> None:
    result = check_regression(expected=False, actual=None)

    assert result.passed is False
    assert result.actual is None
    assert "No verdict" in result.message
