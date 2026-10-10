
from abc import ABC, abstractmethod
from dataclasses import dataclass

from redteam.feedback.schema import CategoryFeedback


@dataclass(frozen=True)
class GeneratedAttack:
    name: str
    category: str
    description: str
    payload: str
    severity: str


class AttackGenerator(ABC):
    @abstractmethod
    def generate(
        self,
        *,
        category: str,
        target_context: str,
        count: int = 1,
        feedback: list[CategoryFeedback] | None = None,
    ) -> list[GeneratedAttack]:
        """Generate adversarial test cases."""
        raise NotImplementedError

