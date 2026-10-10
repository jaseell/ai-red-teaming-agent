from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class TargetResponse:
    content: str
    model: str | None = None
    raw_response: object | None = None


class TargetAdapter(ABC):
    @abstractmethod
    def send(self, prompt: str) -> TargetResponse:
        """Send a prompt to the target AI system."""
        raise NotImplementedError
