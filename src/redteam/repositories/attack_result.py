from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from redteam.models.attack import Attack
from redteam.models.attack_result import AttackResult
from redteam.models.target import Target


class AttackResultRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        attack: Attack,
        target: Target,
        prompt: str,
        response: str,
        model: str | None = None,
        latency_ms: float | None = None,
        execution_status: str = "success",
        error_message: str | None = None,
        attack_succeeded: bool | None = None,
        severity: str | None = None,
        confidence: float | None = None,
        reasoning: str | None = None,
        executed_at: datetime | None = None,
    ) -> AttackResult:
        result = AttackResult(
            attack_id=attack.id,
            target_id=target.id,
            prompt=prompt,
            response=response,
            model=model,
            latency_ms=latency_ms,
            execution_status=execution_status,
            error_message=error_message,
            attack_succeeded=attack_succeeded,
            severity=severity,
            confidence=confidence,
            reasoning=reasoning,
            executed_at=executed_at or datetime.now(UTC),
        )

        self.db.add(result)
        self.db.flush()
        self.db.refresh(result)

        return result

    def get_by_id(self, result_id: int) -> AttackResult | None:
        statement = select(AttackResult).where(
            AttackResult.id == result_id,
        )

        return self.db.scalar(statement)

    def list_by_attack(
        self,
        attack: Attack,
    ) -> list[AttackResult]:
        statement = (
            select(AttackResult)
            .where(AttackResult.attack_id == attack.id)
            .order_by(AttackResult.id)
        )

        return list(self.db.scalars(statement).all())

    def list_by_target(
        self,
        target: Target,
    ) -> list[AttackResult]:
        statement = (
            select(AttackResult)
            .where(AttackResult.target_id == target.id)
            .order_by(AttackResult.id)
        )

        return list(self.db.scalars(statement).all())

    def list_recent(
        self,
        limit: int = 100,
    ) -> list[AttackResult]:
        statement = (
            select(AttackResult)
            .order_by(AttackResult.executed_at.desc())
            .limit(limit)
        )

        return list(self.db.scalars(statement).all())
