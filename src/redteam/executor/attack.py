from dataclasses import dataclass
from datetime import UTC, datetime

from redteam.adapters.base import TargetAdapter, TargetResponse
from redteam.models.attack import Attack


@dataclass(frozen=True)
class AttackExecutionResult:
    attack_id: int
    attack_name: str
    prompt: str
    response: TargetResponse
    executed_at: datetime


class AttackExecutor:
    def __init__(self, adapter: TargetAdapter) -> None:
        self.adapter = adapter

    def execute(self, attack: Attack) -> AttackExecutionResult:
        response = self.adapter.send(attack.payload)

        return AttackExecutionResult(
            attack_id=attack.id,
            attack_name=attack.name,
            prompt=attack.payload,
            response=response,
            executed_at=datetime.now(UTC),
        )
