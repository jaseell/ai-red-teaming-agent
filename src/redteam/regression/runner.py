
from dataclasses import dataclass

import httpx

from redteam.evaluator.base import Evaluator, SecurityEvaluation
from redteam.regression.cases import REGRESSION_CASES, RegressionCase
from redteam.regression.checker import (
    RegressionCheckResult,
    check_regression,
)


@dataclass(frozen=True)
class RegressionCaseResult:
    case_name: str
    category: str
    check: RegressionCheckResult
    evaluation: SecurityEvaluation | None
    error: str | None = None


class RegressionRunner:
    """Run known-answer regression cases against an evaluator."""

    def __init__(self, evaluator: Evaluator) -> None:
        self.evaluator = evaluator

    def run(
        self,
        cases: tuple[RegressionCase, ...] = REGRESSION_CASES,
    ) -> list[RegressionCaseResult]:
        results: list[RegressionCaseResult] = []

        for case in cases:
            try:
                evaluation = self.evaluator.evaluate(
                    attack_payload=case.attack_payload,
                    target_response=case.target_response,
                )
            except (
                httpx.HTTPError,
                TypeError,
                ValueError,
                KeyError,
            ) as exc:
                check = check_regression(
                    expected=case.expected_attack_succeeded,
                    actual=None,
                )
                results.append(
                    RegressionCaseResult(
                        case_name=case.name,
                        category=case.category,
                        check=check,
                        evaluation=None,
                        error=f"{type(exc).__name__}: {exc}",
                    )
                )
                continue

            check = check_regression(
                expected=case.expected_attack_succeeded,
                actual=evaluation.attack_succeeded,
            )

            results.append(
                RegressionCaseResult(
                    case_name=case.name,
                    category=case.category,
                    check=check,
                    evaluation=evaluation,
                )
            )

        return results

