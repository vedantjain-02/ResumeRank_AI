"""add final scoring breakdown columns to ranking_results

Revision ID: 0005
Revises: 0004
Create Date: 2026-09-11
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("ranking_results", sa.Column("bm25_score", sa.Float(), nullable=True))
    op.add_column("ranking_results", sa.Column("vector_score", sa.Float(), nullable=True))
    op.add_column("ranking_results", sa.Column("hybrid_score", sa.Float(), nullable=True))
    op.add_column("ranking_results", sa.Column("score_breakdown", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("ranking_results", "score_breakdown")
    op.drop_column("ranking_results", "hybrid_score")
    op.drop_column("ranking_results", "vector_score")
    op.drop_column("ranking_results", "bm25_score")