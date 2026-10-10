
from redteam.regression.cases import REGRESSION_CASES, RegressionCase


def test_regression_cases_are_defined() -> None:
    assert len(REGRESSION_CASES) == 3


def test_regression_case_names_are_unique() -> None:
    names = [case.name for case in REGRESSION_CASES]

    assert len(names) == len(set(names))


def test_regression_cases_have_required_fields() -> None:
    for case in REGRESSION_CASES:
        assert isinstance(case, RegressionCase)
        assert case.name.strip()
        assert case.category.strip()
        assert case.attack_payload.strip()
        assert case.target_response.strip()
        assert isinstance(case.expected_attack_succeeded, bool)


def test_regression_cases_cover_expected_outcomes() -> None:
    expected_outcomes = {
        case.expected_attack_succeeded
        for case in REGRESSION_CASES
    }

    assert expected_outcomes == {False, True}
