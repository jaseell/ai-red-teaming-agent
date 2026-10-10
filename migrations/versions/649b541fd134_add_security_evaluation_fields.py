"""Add security evaluation fields

Revision ID: 649b541fd134
Revises: 24f59c7154d9
Create Date: 2026-09-06 10:57:19.296247

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '649b541fd134'
down_revision: str | Sequence[str] | None = '24f59c7154d9'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "attack_results",
        sa.Column("attack_succeeded", sa.Boolean(), nullable=True),
    )
    op.add_column(
        "attack_results",
        sa.Column("severity", sa.String(length=20), nullable=True),
    )
    op.add_column(
        "attack_results",
        sa.Column("confidence", sa.Float(), nullable=True),
    )
    op.add_column(
        "attack_results",
        sa.Column("reasoning", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("attack_results", "reasoning")
    op.drop_column("attack_results", "confidence")
    op.drop_column("attack_results", "severity")
    op.drop_column("attack_results", "attack_succeeded")
