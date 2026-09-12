"""create initial tables

Revision ID: 0001
Revises:
Create Date: 2026-09-11

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "candidates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("resume_file_path", sa.String(1024), nullable=True),
        sa.Column("resume_text", sa.Text(), nullable=True),
        sa.Column("skills", sa.Text(), nullable=True),
        sa.Column("years_of_experience", sa.Float(), nullable=False, default=0.0),
        sa.Column("education", sa.Text(), nullable=True),
        sa.Column("certifications", sa.Text(), nullable=True),
        sa.Column("work_experience", sa.Text(), nullable=True),
        sa.Column("resume_embedding", Vector(384), nullable=True),
        sa.Column("resume_upload_date", sa.DateTime(), nullable=False),
        sa.Column("is_seed", sa.Boolean(), default=False),
    )

    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("required_skills", sa.Text(), nullable=False),
        sa.Column("preferred_skills", sa.Text(), nullable=True),
        sa.Column("minimum_experience", sa.Float(), nullable=True, default=0.0),
        sa.Column("education_requirement", sa.Text(), nullable=True),
        sa.Column("responsibilities", sa.Text(), nullable=True),
        sa.Column("certifications_required", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("is_mandatory_requirements", sa.Text(), nullable=True),
    )

    op.create_table(
        "ranking_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("candidate_id", sa.Integer(), sa.ForeignKey("candidates.id"), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("match_score", sa.Float(), nullable=False),
        sa.Column("skills_score", sa.Float(), nullable=False, default=0.0),
        sa.Column("experience_score", sa.Float(), nullable=False, default=0.0),
        sa.Column("semantic_score", sa.Float(), nullable=False, default=0.0),
        sa.Column("education_score", sa.Float(), nullable=False, default=0.0),
        sa.Column("matched_skills", sa.JSON(), nullable=True),
        sa.Column("missing_skills", sa.JSON(), nullable=True),
        sa.Column("experience_match", sa.String(50), nullable=True),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_index("ix_candidates_id", "candidates", ["id"])
    op.create_index("ix_candidates_name", "candidates", ["name"])
    op.create_index("ix_candidates_email", "candidates", ["email"])
    op.create_index("ix_jobs_id", "jobs", ["id"])
    op.create_index("ix_ranking_results_id", "ranking_results", ["id"])
    op.create_index("ix_ranking_results_job_id", "ranking_results", ["job_id"])
    op.create_index("ix_ranking_results_candidate_id", "ranking_results", ["candidate_id"])


def downgrade() -> None:
    op.drop_index("ix_ranking_results_candidate_id", table_name="ranking_results")
    op.drop_index("ix_ranking_results_job_id", table_name="ranking_results")
    op.drop_index("ix_ranking_results_id", table_name="ranking_results")
    op.drop_index("ix_jobs_id", table_name="jobs")
    op.drop_index("ix_candidates_email", table_name="candidates")
    op.drop_index("ix_candidates_name", table_name="candidates")
    op.drop_index("ix_candidates_id", table_name="candidates")
    op.drop_table("ranking_results")
    op.drop_table("jobs")
    op.drop_table("candidates")