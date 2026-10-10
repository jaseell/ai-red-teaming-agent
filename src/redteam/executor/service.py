from time import perf_counter

from sqlalchemy.orm import Session

from redteam.adapters.base import TargetAdapter
from redteam.evaluator.base import Evaluator
from redteam.executor.attack import AttackExecutionResult, AttackExecutor
from redteam.models.attack import Attack
from redteam.models.target import Target
from redteam.repositories.attack_result import AttackResultRepository


class AttackExecutionService:
    def __init__(
        self,
        db_session: Session,
        adapter: TargetAdapter,
        evaluator: Evaluator,
    ) -> None:
        self.result_repository = AttackResultRepository(db_session)
        self.executor = AttackExecutor(adapter)
        self.evaluator = evaluator

    def execute(
        self,
        *,
        attack: Attack,
        target: Target,
    ) -> AttackExecutionResult:
        started_at = perf_counter()

        execution_result = self.executor.execute(attack)

        latency_ms = (perf_counter() - started_at) * 1000

        evaluation = self.evaluator.evaluate(
            attack_payload=execution_result.prompt,
            target_response=execution_result.response.content,
        )

        self.result_repository.create(
            attack=attack,
            target=target,
            prompt=execution_result.prompt,
            response=execution_result.response.content,
            model=execution_result.response.model,
            latency_ms=latency_ms,
            execution_status="success",
            executed_at=execution_result.executed_at,
            attack_succeeded=evaluation.attack_succeeded,
            severity=evaluation.severity,
            confidence=evaluation.confidence,
            reasoning=evaluation.reasoning,
        )

        return execution_result
