from sqlalchemy import select
from sqlalchemy.orm import Session

from redteam.feedback.schema import CategoryFeedback
from redteam.models.attack import Attack
from redteam.models.attack_result import AttackResult


class FeedbackService:
    def __init__(self, db_session: Session) -> None:
        self.db = db_session

    def summarize_by_category(self) -> list[CategoryFeedback]:
        statement = (
            select(Attack.category, AttackResult.attack_succeeded)
            .join(AttackResult, AttackResult.attack_id == Attack.id)
            .where(AttackResult.execution_status == "success")
            .order_by(Attack.category)
        )

        rows = self.db.execute(statement).all()
        summaries: dict[str, dict[str, int]] = {}

        for category, succeeded in rows:
            counts = summaries.setdefault(
                category,
                {"total": 0, "succeeded": 0, "failed": 0, "unscored": 0},
            )
            counts["total"] += 1

            if succeeded is True:
                counts["succeeded"] += 1
            elif succeeded is False:
                counts["failed"] += 1
            else:
                counts["unscored"] += 1

        feedback: list[CategoryFeedback] = []

        for category, counts in summaries.items():
            scored = counts["succeeded"] + counts["failed"]
            success_rate = (
                counts["succeeded"] / scored if scored > 0 else None
            )

            feedback.append(
                CategoryFeedback(
                    category=category,
                    total=counts["total"],
                    succeeded=counts["succeeded"],
                    failed=counts["failed"],
                    unscored=counts["unscored"],
                    success_rate=success_rate,
                )
            )

        return feedback
