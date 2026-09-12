from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.database import Base


class Candidate(Base):
    """Candidate record.

    Required columns (names are part of the public contract):
        id, name, phone_number, career_summary, total_experience_years,
        seniority_level, job_title, functional_expertise, leadership,
        education, capability_tags

    Supplementary columns (support semantic matching and resume viewing):
        resume_embedding, resume_text, resume_file_path, is_seed, created_at
    """

    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    career_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    total_experience_years: Mapped[Optional[float]] = mapped_column(Float, nullable=True, index=True)
    seniority_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    job_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)

    functional_expertise: Mapped[Optional[List[Any]]] = mapped_column(JSONB, nullable=True)
    leadership: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    education: Mapped[Optional[List[Any]]] = mapped_column(JSONB, nullable=True)
    capability_tags: Mapped[Optional[List[Any]]] = mapped_column(JSONB, nullable=True)

    resume_embedding: Mapped[Optional[Any]] = mapped_column(Vector(384), nullable=True)
    resume_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resume_file_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    is_seed: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    rankings = relationship(
        "RankingResult",
        back_populates="candidate",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Candidate(id={self.id}, name={self.name}, job_title={self.job_title})>"