from datetime import date
from typing import Any

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from redteam.models.attack_result import AttackResult


class AttackSuccessTrendService:
    """Build daily attack success metrics from persisted results."""

    def __init__(self, db_session: Session) -> None:
        self.db = db_session

    def build_trend(self) -> list[dict[str, Any]]:
        day = func.date(AttackResult.executed_at)

        statement = (
            select(
                day.label("execution_date"),
                func.count(AttackResult.id).label("executions"),
                func.sum(
                    case(
                        (
                            AttackResult.attack_succeeded.is_not(None),
                            1,
                        ),
                        else_=0,
                    )
                ).label("scored"),
                func.sum(
                    case(
                        (
                            AttackResult.attack_succeeded.is_(True),
                            1,
                        ),
                        else_=0,
                    )
                ).label("successful_attacks"),
            )
            .where(
                AttackResult.execution_status == "success"
            )
            .group_by(day)
            .order_by(day)
        )

        rows = self.db.execute(statement).all()

        trend = []

        for execution_date, executions, scored, succeeded in rows:
            scored_count = scored or 0
            succeeded_count = succeeded or 0

            trend.append(
                {
                    "date": (
                        execution_date.isoformat()
                        if isinstance(execution_date, date)
                        else str(execution_date)
                    ),
                    "executions": executions,
                    "scored": scored_count,
                    "successful_attacks": succeeded_count,
                    "attack_success_rate": (
                        succeeded_count / scored_count
                        if scored_count
                        else None
                    ),
                }
            )

        return trend
