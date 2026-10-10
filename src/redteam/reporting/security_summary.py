import json
from pathlib import Path
from typing import Any

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from redteam.models.attack import Attack
from redteam.models.attack_result import AttackResult


class SecuritySummaryService:
    """Build a security summary from persisted attack results."""

    def __init__(self, db_session: Session) -> None:
        self.db = db_session

    def build_summary(self) -> dict[str, Any]:
        total = self.db.scalar(
            select(func.count(AttackResult.id))
        ) or 0

        execution_success = self.db.scalar(
            select(func.count(AttackResult.id)).where(
                AttackResult.execution_status == "success"
            )
        ) or 0

        execution_failed = total - execution_success

        attack_succeeded = self.db.scalar(
            select(func.count(AttackResult.id)).where(
                AttackResult.execution_status == "success",
                AttackResult.attack_succeeded.is_(True),
            )
        ) or 0

        attack_failed = self.db.scalar(
            select(func.count(AttackResult.id)).where(
                AttackResult.execution_status == "success",
                AttackResult.attack_succeeded.is_(False),
            )
        ) or 0

        unscored = self.db.scalar(
            select(func.count(AttackResult.id)).where(
                AttackResult.execution_status == "success",
                AttackResult.attack_succeeded.is_(None),
            )
        ) or 0

        category_rows = self.db.execute(
            select(
                Attack.category,
                func.count(AttackResult.id).label("total"),
                func.sum(
                    case(
                        (AttackResult.attack_succeeded.is_(True), 1),
                        else_=0,
                    )
                ).label("succeeded"),
                func.sum(
                    case(
                        (AttackResult.attack_succeeded.is_not(None), 1),
                        else_=0,
                    )
                ).label("scored"),
            )
            .join(AttackResult, AttackResult.attack_id == Attack.id)
            .where(AttackResult.execution_status == "success")
            .group_by(Attack.category)
            .order_by(Attack.category)
        ).all()

        categories = [
            {
                "category": category,
                "total": count,
                "succeeded": succeeded,
                "success_rate": succeeded / scored if scored else None,
            }
            for category, count, succeeded, scored in category_rows
        ]

        severity_rows = self.db.execute(
            select(
                AttackResult.severity,
                func.count(AttackResult.id),
            )
            .where(
                AttackResult.execution_status == "success",
                AttackResult.attack_succeeded.is_(True),
            )
            .group_by(AttackResult.severity)
            .order_by(AttackResult.severity)
        ).all()

        return {
            "summary": {
                "total_executions": total,
                "execution_successes": execution_success,
                "execution_failures": execution_failed,
                "successful_attacks": attack_succeeded,
                "failed_attacks": attack_failed,
                "unscored_results": unscored,
            },
            "by_category": categories,
            "successful_attacks_by_severity": [
                {"severity": severity, "count": count}
                for severity, count in severity_rows
            ],
        }


def build_security_summary_report(
    db_session: Session,
) -> dict[str, Any]:
    """Build a JSON-serializable security summary report."""
    return SecuritySummaryService(db_session).build_summary()


def write_security_summary_report(
    db_session: Session,
    output_path: str | Path = "reports/security-summary.json",
) -> Path:
    """Write the security summary to a JSON file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    report = build_security_summary_report(db_session)
    path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path
