from redteam.evaluator.base import Evaluator, SecurityEvaluation


class MockEvaluator(Evaluator):
    def evaluate(
        self,
        *,
        attack_payload: str,
        target_response: str,
    ) -> SecurityEvaluation:
        return SecurityEvaluation(
            attack_succeeded=False,
            severity="low",
            confidence=0.95,
            reasoning="The target refused the attack.",
        )
