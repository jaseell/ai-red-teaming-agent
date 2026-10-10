from sqlalchemy.orm import Session

from redteam.reporting.security_summary import SecuritySummaryService
from redteam.repositories.attack import AttackRepository
from redteam.repositories.attack_result import AttackResultRepository
from redteam.repositories.target import TargetRepository


def test_security_summary_counts_results_by_category(
    db_session: Session,
) -> None:
    attack_repository = AttackRepository(db_session)
    target_repository = TargetRepository(db_session)
    result_repository = AttackResultRepository(db_session)

    attack = attack_repository.create(
        name="Security Summary Test Attack",
        category="prompt_injection",
        description="Attack for security summary testing.",
        payload="Test payload",
        severity="high",
    )

    target = target_repository.create(
        name="Security Summary Test Target",
        target_type="llm",
        endpoint="http://localhost:8000",
    )

    db_session.flush()

    for succeeded in (True, False, None):
        result_repository.create(
            attack=attack,
            target=target,
            prompt="Test prompt",
            response="Test response",
            execution_status="success",
            attack_succeeded=succeeded,
            severity="high",
        )

    result_repository.create(
        attack=attack,
        target=target,
        prompt="Failed execution",
        response="",
        execution_status="error",
        error_message="Test execution error",
        attack_succeeded=None,
        severity="high",
    )

    db_session.flush()

    summary = SecuritySummaryService(db_session).build_summary()

    assert summary["summary"]["total_executions"] == 4
    assert summary["summary"]["execution_successes"] == 3
    assert summary["summary"]["execution_failures"] == 1
    assert summary["summary"]["successful_attacks"] == 1
    assert summary["summary"]["failed_attacks"] == 1
    assert summary["summary"]["unscored_results"] == 1

    assert summary["by_category"] == [
        {
            "category": "prompt_injection",
            "total": 3,
            "succeeded": 1,
            "success_rate": 0.5,
        }
    ]

    assert summary["successful_attacks_by_severity"] == [
        {"severity": "high", "count": 1}
    ]


def test_security_summary_writes_json_report(
    db_session: Session,
    tmp_path,
) -> None:
    import json

    from redteam.reporting.security_summary import (
        write_security_summary_report,
    )

    output_path = tmp_path / "security-summary.json"

    written_path = write_security_summary_report(
        db_session,
        output_path,
    )

    assert written_path == output_path
    assert output_path.exists()

    report = json.loads(output_path.read_text(encoding="utf-8"))

    assert "summary" in report
    assert "by_category" in report
    assert "successful_attacks_by_severity" in report
    assert report["summary"]["total_executions"] == 0
