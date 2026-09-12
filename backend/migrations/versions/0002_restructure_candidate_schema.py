"""restructure candidates table to JSONB-based schema

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-11
"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop dependent table first (ranking_results FK → candidates)
    op.drop_table("ranking_results")
    # Drop old candidates table
    op.drop_table("candidates")

    # ── New candidates table with JSONB columns ───────────────────────────
    op.create_table(
        "candidates",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("phone_number", sa.String(50), nullable=True),
        sa.Column("career_summary", sa.Text(), nullable=True),
        sa.Column("total_experience_years", sa.Float(), nullable=True),
        sa.Column("seniority_level", sa.String(50), nullable=True),
        sa.Column("job_title", sa.String(255), nullable=True),
        sa.Column("functional_expertise", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("leadership", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("education", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("capability_tags", sa.dialects.postgresql.JSONB(), nullable=True),
        # Supplementary columns (not in public contract, support semantic matching & resume viewing)
        sa.Column("resume_embedding", Vector(384), nullable=True),
        sa.Column("resume_text", sa.Text(), nullable=True),
        sa.Column("resume_file_path", sa.String(1024), nullable=True),
        sa.Column("is_seed", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # Indexes
    op.create_index("ix_candidates_id", "candidates", ["id"])
    op.create_index("ix_candidates_name", "candidates", ["name"])
    op.create_index("ix_candidates_phone_number", "candidates", ["phone_number"])
    op.create_index("ix_candidates_total_experience_years", "candidates", ["total_experience_years"])
    op.create_index("ix_candidates_seniority_level", "candidates", ["seniority_level"])
    op.create_index("ix_candidates_job_title", "candidates", ["job_title"])

    # GIN indexes for JSONB full-text / containment queries
    op.create_index("ix_candidates_capability_tags_gin", "candidates", ["capability_tags"], postgresql_using="gin")
    op.create_index("ix_candidates_functional_expertise_gin", "candidates", ["functional_expertise"], postgresql_using="gin")
    op.create_index("ix_candidates_education_gin", "candidates", ["education"], postgresql_using="gin")
    op.create_index("ix_candidates_leadership_gin", "candidates", ["leadership"], postgresql_using="gin")

    # ── Recreate ranking_results (FKs unchanged) ──────────────────────────
    op.create_table(
        "ranking_results",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("candidate_id", sa.Integer(), sa.ForeignKey("candidates.id"), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("match_score", sa.Float(), nullable=False),
        sa.Column("skills_score", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("experience_score", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("semantic_score", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("education_score", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("matched_skills", sa.dialects.postgresql.JSON(), nullable=True),
        sa.Column("missing_skills", sa.dialects.postgresql.JSON(), nullable=True),
        sa.Column("experience_match", sa.String(50), nullable=True),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_index("ix_ranking_results_job_id", "ranking_results", ["job_id"])
    op.create_index("ix_ranking_results_candidate_id", "ranking_results", ["candidate_id"])


def downgrade() -> None:
    op.drop_index("ix_ranking_results_candidate_id", table_name="ranking_results")
    op.drop_index("ix_ranking_results_job_id", table_name="ranking_results")
    op.drop_table("ranking_results")

    for idx in [
        "ix_candidates_capability_tags_gin",
        "ix_candidates_functional_expertise_gin",
        "ix_candidates_education_gin",
        "ix_candidates_leadership_gin",
        "ix_candidates_job_title",
        "ix_candidates_seniority_level",
        "ix_candidates_total_experience_years",
        "ix_candidates_phone_number",
        "ix_candidates_name",
        "ix_candidates_id",
    ]:
        op.drop_index(idx, table_name="candidates")
    op.drop_table("candidates")

    # Recreate original old-style candidates table (from 0001)
    op.create_table(
        "candidates",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("resume_file_path", sa.String(1024), nullable=True),
        sa.Column("resume_text", sa.Text(), nullable=True),
        sa.Column("skills", sa.Text(), nullable=True),
        sa.Column("years_of_experience", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("education", sa.Text(), nullable=True),
        sa.Column("certifications", sa.Text(), nullable=True),
        sa.Column("work_experience", sa.Text(), nullable=True),
        sa.Column("resume_embedding", Vector(384), nullable=True),
        sa.Column("resume_upload_date", sa.DateTime(), nullable=False),
        sa.Column("is_seed", sa.Boolean(), server_default=sa.text("false")),
    )

    op.create_index("ix_candidates_id", "candidates", ["id"])
    op.create_index("ix_candidates_name", "candidates", ["name"])
    op.create_index("ix_candidates_email", "candidates", ["email"])

    op.create_table(
        "ranking_results",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("candidate_id", sa.Integer(), sa.ForeignKey("candidates.id"), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("match_score", sa.Float(), nullable=False),
        sa.Column("skills_score", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("experience_score", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("semantic_score", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("education_score", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("matched_skills", sa.dialects.postgresql.JSON(), nullable=True),
        sa.Column("missing_skills", sa.dialects.postgresql.JSON(), nullable=True),
        sa.Column("experience_match", sa.String(50), nullable=True),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_ranking_results_id", "ranking_results", ["id"])
    op.create_index("ix_ranking_results_job_id", "ranking_results", ["job_id"])
    op.create_index("ix_ranking_results_candidate_id", "ranking_results", ["candidate_id"])