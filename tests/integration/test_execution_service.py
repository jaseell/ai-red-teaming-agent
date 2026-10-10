from sqlalchemy.orm import Session

from redteam.adapters.mock import MockTargetAdapter
from redteam.executor.service import AttackExecutionService
from redteam.repositories.attack import AttackRepository
from redteam.repositories.attack_result import AttackResultRepository
from redteam.repositories.target import TargetRepository
from tests.fakes.evaluator import MockEvaluator


def test_execution_service_persists_result(
    db_session: Session,
) -> None:
    attack_repository = AttackRepository(db_session)
    target_repository = TargetRepository(db_session)

    attack = attack_repository.create(
        name="Service Test Attack",
        category="prompt_injection",
        description="Attack used for execution service testing.",
        payload="Test attack payload",
        severity="medium",
    )

    target = target_repository.create(
        name="Service Test Target",
        target_type="llm",
        endpoint="http://localhost:8000",
    )

    db_session.commit()

    service = AttackExecutionService(
    db_session=db_session,
    adapter=MockTargetAdapter(),
    evaluator=MockEvaluator(),
)

    execution_result = service.execute(
        attack=attack,
        target=target,
    )

    db_session.commit()

    assert execution_result.attack_id == attack.id
    assert execution_result.attack_name == attack.name
    assert execution_result.prompt == "Test attack payload"
    assert execution_result.response.content == "Mock target response"

    result_repository = AttackResultRepository(db_session)

    results = result_repository.list_by_attack(attack)

    assert len(results) == 1

    stored_result = results[0]

    assert stored_result.attack_id == attack.id
    assert stored_result.target_id == target.id
    assert stored_result.prompt == "Test attack payload"
    assert stored_result.response == "Mock target response"
    assert stored_result.model == "mock-model"
    assert stored_result.execution_status == "success"
    assert stored_result.latency_ms is not None
    assert stored_result.latency_ms >= 0
    assert stored_result.attack_succeeded is False
    assert stored_result.severity == "low"
    assert stored_result.confidence == 0.95
    assert stored_result.reasoning == "The target refused the attack."
