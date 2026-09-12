"""add server default to jobs.created_at

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-11
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "jobs",
        "created_at",
        existing_type=sa.DateTime(),
        nullable=False,
        server_default=sa.func.now(),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "jobs",
        "created_at",
        existing_type=sa.DateTime(),
        nullable=False,
        server_default=None,
        existing_nullable=False,
    )