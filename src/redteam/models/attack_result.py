from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from redteam.models.base import Base


class AttackResult(Base):
    __tablename__ = "attack_results"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    attack_id: Mapped[int] = mapped_column(
        ForeignKey("attacks.id"),
        nullable=False,
    )

    target_id: Mapped[int] = mapped_column(
        ForeignKey("targets.id"),
        nullable=False,
    )

    prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    response: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    model: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    latency_ms: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    execution_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    attack_succeeded: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    severity: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    reasoning: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
