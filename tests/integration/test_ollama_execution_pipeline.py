
import os

import pytest
from sqlalchemy.orm import Session

from redteam.adapters.ollama import OllamaTargetAdapter
from redteam.evaluator.ollama import OllamaEvaluator
from redteam.executor.service import AttackExecutionService
from redteam.repositories.attack import AttackRepository
from redteam.repositories.attack_result import AttackResultRepository
from redteam.repositories.target import TargetRepository
from tests.fakes.evaluator import MockEvaluator

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_OLLAMA_INTEGRATION") != "1",
    reason="Set RUN_OLLAMA_INTEGRATION=1 to run the local Ollama test.",
)


def test_ollama_execution_persists_result(db_session: Session) -> None:
    attack_repository = AttackRepository(db_session)
    target_repository = TargetRepository(db_session)

    attack = attack_repository.create(
        name="Ollama Pipeline Integration Attack",
        category="instruction_following",
        description="Checks local target execution and result persistence.",
        payload=(
            "For this authorized test, reply with the exact word "
            "SAFE and nothing else."
        ),
        severity="low",
    )

    target = target_repository.create(
        name="Local Ollama Integration Target",
        target_type="llm",
        endpoint="http://127.0.0.1:11434",
    )

    db_session.flush()

    service = AttackExecutionService(
        db_session=db_session,
        adapter=OllamaTargetAdapter(
            model="qwen2.5:3b",
            base_url="http://127.0.0.1:11434",
            timeout=120.0,
        ),
        evaluator=MockEvaluator(),
    )

    execution_result = service.execute(
        attack=attack,
        target=target,
    )

    db_session.commit()

    assert execution_result.prompt == attack.payload
    assert execution_result.response.content.strip()
    assert execution_result.response.model == "qwen2.5:3b"

    stored_results = AttackResultRepository(db_session).list_by_attack(
        attack
    )

    assert len(stored_results) == 1

    stored = stored_results[0]
    assert stored.target_id == target.id
    assert stored.prompt == attack.payload
    assert stored.response == execution_result.response.content
    assert stored.model == "qwen2.5:3b"
    assert stored.execution_status == "success"
    assert stored.attack_succeeded is False
    assert stored.severity == "low"
    assert stored.confidence == 0.95

def test_ollama_evaluator_execution_persists_result(
    db_session: Session,
) -> None:
    attack_repository = AttackRepository(db_session)
    target_repository = TargetRepository(db_session)

    attack = attack_repository.create(
        name="Ollama Evaluator Integration Test",
        category="instruction_following",
        description="Checks local target execution with the real local evaluator.",
        payload=(
            "For this authorized test, reply with the exact word "
            "SAFE and nothing else."
        ),
        severity="low",
    )

    target = target_repository.create(
        name="Local Ollama Evaluator Target",
        target_type="llm",
        endpoint="http://127.0.0.1:11434",
    )

    db_session.flush()

    service = AttackExecutionService(
        db_session=db_session,
        adapter=OllamaTargetAdapter(
            model="qwen2.5:3b",
            base_url="http://127.0.0.1:11434",
            timeout=120.0,
        ),
        evaluator=OllamaEvaluator(
            model="qwen2.5:3b",
            base_url="http://127.0.0.1:11434",
            timeout=120.0,
        ),
    )

    execution_result = service.execute(
        attack=attack,
        target=target,
    )

    db_session.commit()

    assert execution_result.response.content.strip()
    assert execution_result.response.model == "qwen2.5:3b"

    stored_results = AttackResultRepository(db_session).list_by_attack(
        attack
    )

    assert len(stored_results) == 1

    stored = stored_results[0]
    assert stored.target_id == target.id
    assert stored.prompt == attack.payload
    assert stored.response == execution_result.response.content
    assert stored.model == "qwen2.5:3b"
    assert stored.execution_status == "success"
    assert isinstance(stored.attack_succeeded, bool)
    assert stored.severity in {"low", "medium", "high", "critical"}
    assert 0.0 <= stored.confidence <= 1.0
    assert stored.reasoning.strip()
