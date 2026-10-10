from sqlalchemy.orm import Session

from redteam.feedback.service import FeedbackService
from redteam.repositories.attack import AttackRepository
from redteam.repositories.attack_result import AttackResultRepository
from redteam.repositories.target import TargetRepository


def test_feedback_service_summarizes_category_results(
    db_session: Session,
) -> None:
    attack_repository = AttackRepository(db_session)
    target_repository = TargetRepository(db_session)
    result_repository = AttackResultRepository(db_session)

    attack = attack_repository.create(
        name="Feedback Test Attack",
        category="feedback_service_test",
        description="Attack for feedback testing.",
        payload="Test payload",
        severity="medium",
    )

    target = target_repository.create(
        name="Feedback Test Target",
        target_type="llm",
        endpoint="http://localhost:8000",
    )

    db_session.flush()

    result_repository.create(
        attack=attack,
        target=target,
        prompt="Payload 1",
        response="Response 1",
        execution_status="success",
        attack_succeeded=True,
    )

    result_repository.create(
        attack=attack,
        target=target,
        prompt="Payload 2",
        response="Response 2",
        execution_status="success",
        attack_succeeded=False,
    )

    result_repository.create(
        attack=attack,
        target=target,
        prompt="Payload 3",
        response="Response 3",
        execution_status="success",
        attack_succeeded=None,
    )

    db_session.flush()

    service = FeedbackService(db_session)
    summaries = service.summarize_by_category()

    matching_summaries = [
        summary
        for summary in summaries
        if summary.category == "feedback_service_test"
    ]

    assert len(matching_summaries) == 1

    summary = matching_summaries[0]
    assert summary.total == 3
    assert summary.succeeded == 1
    assert summary.failed == 1
    assert summary.unscored == 1
    assert summary.success_rate == 0.5


def test_feedback_service_returns_none_rate_when_unscored(
    db_session: Session,
) -> None:
    attack_repository = AttackRepository(db_session)
    target_repository = TargetRepository(db_session)
    result_repository = AttackResultRepository(db_session)

    attack = attack_repository.create(
        name="Unscored Feedback Attack",
        category="unscored_feedback_test",
        description="Attack without an evaluation.",
        payload="Test payload",
        severity="low",
    )

    target = target_repository.create(
        name="Unscored Feedback Target",
        target_type="llm",
        endpoint="http://localhost:8000",
    )

    db_session.flush()

    result_repository.create(
        attack=attack,
        target=target,
        prompt="Payload",
        response="Response",
        execution_status="success",
        attack_succeeded=None,
    )

    db_session.flush()

    service = FeedbackService(db_session)
    summaries = service.summarize_by_category()

    matching_summaries = [
        summary
        for summary in summaries
        if summary.category == "unscored_feedback_test"
    ]

    assert len(matching_summaries) == 1

    summary = matching_summaries[0]
    assert summary.total == 1
    assert summary.succeeded == 0
    assert summary.failed == 0
    assert summary.unscored == 1
    assert summary.success_rate is None

