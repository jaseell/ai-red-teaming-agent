from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class SecurityEvaluation:
    attack_succeeded: bool
    severity: str
    confidence: float
    reasoning: str


class Evaluator(ABC):
    @abstractmethod
    def evaluate(
        self,
        *,
        attack_payload: str,
        target_response: str,
    ) -> SecurityEvaluation:
        """Evaluate whether an attack succeeded."""
        raise NotImplementedError
