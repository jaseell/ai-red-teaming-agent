from sqlalchemy.orm import Session

from redteam.repositories.target import TargetRepository


def test_target_crud(db_session: Session) -> None:
    repository = TargetRepository(db_session)

    # CREATE
    target = repository.create(
        name="Local Test LLM",
        target_type="llm",
        endpoint="http://localhost:8000",
        description="Local authorized test target",
    )
    db_session.commit()

    assert target.id is not None
    assert target.name == "Local Test LLM"
    assert target.target_type == "llm"
    assert target.is_active is True

    # READ
    found_by_id = repository.get_by_id(target.id)
    assert found_by_id is not None
    assert found_by_id.name == "Local Test LLM"

    found_by_name = repository.get_by_name("Local Test LLM")
    assert found_by_name is not None
    assert found_by_name.id == target.id

    active_targets = repository.list_active()
    assert len(active_targets) == 1
    assert active_targets[0].id == target.id

    # UPDATE
    updated = repository.update(
        target,
        description="Updated local test target",
        endpoint="http://localhost:8001",
    )
    db_session.commit()

    assert updated.description == "Updated local test target"
    assert updated.endpoint == "http://localhost:8001"

    # DEACTIVATE
    deactivated = repository.deactivate(target)
    db_session.commit()

    assert deactivated.is_active is False

    # Verify inactive target is excluded from active list
    active_targets = repository.list_active()
    assert active_targets == []
