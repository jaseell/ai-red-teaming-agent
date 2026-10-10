
from redteam.evaluator.base import Evaluator, SecurityEvaluation
from redteam.regression.cases import REGRESSION_CASES, RegressionCase
from redteam.regression.runner import RegressionRunner


class FakeEvaluator(Evaluator):
    def __init__(self, verdicts: dict[str, bool]) -> None:
        self.verdicts = verdicts

    def evaluate(
        self,
        *,
        attack_payload: str,
        target_response: str,
    ) -> SecurityEvaluation:
        succeeded = self.verdicts[target_response]

        return SecurityEvaluation(
            attack_succeeded=succeeded,
            severity="low",
            confidence=0.8,
            reasoning="Deterministic test verdict.",
        )


class FailingEvaluator(Evaluator):
    def evaluate(
        self,
        *,
        attack_payload: str,
        target_response: str,
    ) -> SecurityEvaluation:
        raise ValueError("Simulated evaluator failure")


def test_runner_passes_when_all_verdicts_match() -> None:
    evaluator = FakeEvaluator(
        {
            case.target_response: case.expected_attack_succeeded
            for case in REGRESSION_CASES
        }
    )

    results = RegressionRunner(evaluator).run()

    assert len(results) == len(REGRESSION_CASES)
    assert all(result.check.passed for result in results)
    assert all(result.error is None for result in results)


def test_runner_detects_verdict_mismatch() -> None:
    case = REGRESSION_CASES[0]
    evaluator = FakeEvaluator({case.target_response: True})

    results = RegressionRunner(evaluator).run((case,))

    assert len(results) == 1
    assert results[0].check.passed is False
    assert results[0].check.actual is True
    assert results[0].check.expected is False


def test_runner_records_errors_and_continues() -> None:
    first_case = REGRESSION_CASES[0]
    second_case = REGRESSION_CASES[1]
    evaluator = FailingEvaluator()

    results = RegressionRunner(evaluator).run(
        (first_case, second_case)
    )

    assert len(results) == 2
    assert all(not result.check.passed for result in results)
    assert all(result.check.actual is None for result in results)
    assert all(
        result.error is not None
        and "Simulated evaluator failure" in result.error
        for result in results
    )


def test_runner_accepts_an_explicit_case_list() -> None:
    case = RegressionCase(
        name="custom_case",
        category="test",
        attack_payload="Test request",
        target_response="Test response",
        expected_attack_succeeded=False,
    )

    evaluator = FakeEvaluator({"Test response": False})
    results = RegressionRunner(evaluator).run((case,))

    assert len(results) == 1
    assert results[0].case_name == "custom_case"
    assert results[0].check.passed

