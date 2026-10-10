from sqlalchemy.orm import Session

from redteam.repositories.attack import AttackRepository
from redteam.repositories.attack_result import AttackResultRepository
from redteam.repositories.target import TargetRepository


def test_attack_result_repository(
    db_session: Session,
) -> None:
    attack_repository = AttackRepository(db_session)
    target_repository = TargetRepository(db_session)
    result_repository = AttackResultRepository(db_session)

    attack = attack_repository.create(
        name="Result Repository Test Attack",
        category="prompt_injection",
        description="Test attack for result persistence.",
        payload="Test payload",
        severity="high",
    )

    target = target_repository.create(
        name="Result Repository Test Target",
        target_type="llm",
        endpoint="http://localhost:8000/generate",
        description="Test target",
    )

    db_session.commit()

    result = result_repository.create(
        attack=attack,
        target=target,
        prompt="Test prompt",
        response="Test response",
        model="mock-model",
        latency_ms=12.5,
        execution_status="success",
    )

    db_session.commit()

    assert result.id is not None
    assert result.attack_id == attack.id
    assert result.target_id == target.id
    assert result.prompt == "Test prompt"
    assert result.response == "Test response"
    assert result.model == "mock-model"
    assert result.latency_ms == 12.5
    assert result.execution_status == "success"
    assert result.error_message is None

    found = result_repository.get_by_id(result.id)

    assert found is not None
    assert found.id == result.id

    attack_results = result_repository.list_by_attack(attack)

    assert len(attack_results) == 1
    assert attack_results[0].id == result.id

    target_results = result_repository.list_by_target(target)

    assert len(target_results) == 1
    assert target_results[0].id == result.id

    recent_results = result_repository.list_recent()

    assert len(recent_results) >= 1
    assert recent_results[0].id == result.id
