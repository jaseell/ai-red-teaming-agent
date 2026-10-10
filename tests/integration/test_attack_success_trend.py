from datetime import UTC, datetime

from sqlalchemy.orm import Session

from redteam.reporting.attack_success_trend import (
    AttackSuccessTrendService,
)
from redteam.repositories.attack import AttackRepository
from redteam.repositories.attack_result import AttackResultRepository
from redteam.repositories.target import TargetRepository


def test_attack_success_trend_groups_results_by_day(
    db_session: Session,
) -> None:
    attack = AttackRepository(db_session).create(
        name="Trend Test Attack",
        category="prompt_injection",
        description="Attack for trend testing.",
        payload="Test payload",
        severity="high",
    )

    target = TargetRepository(db_session).create(
        name="Trend Test Target",
        target_type="llm",
        endpoint="http://localhost:8000",
    )

    db_session.flush()

    repository = AttackResultRepository(db_session)

    common = {
        "attack": attack,
        "target": target,
        "prompt": "Test prompt",
        "response": "Test response",
        "execution_status": "success",
    }

    repository.create(
        **common,
        attack_succeeded=True,
        executed_at=datetime(2026, 1, 10, 10, tzinfo=UTC),
    )

    repository.create(
        **common,
        attack_succeeded=False,
        executed_at=datetime(2026, 1, 10, 11, tzinfo=UTC),
    )

    repository.create(
        **common,
        attack_succeeded=None,
        executed_at=datetime(2026, 1, 10, 12, tzinfo=UTC),
    )

    db_session.flush()

    trend = AttackSuccessTrendService(db_session).build_trend()

    assert trend == [
        {
            "date": "2026-01-10",
            "executions": 3,
            "scored": 2,
            "successful_attacks": 1,
            "attack_success_rate": 0.5,
        }
    ]
