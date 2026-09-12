from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RankingResult(Base):
    __tablename__ = "ranking_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    candidate_id: Mapped[int] = mapped_column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    match_score: Mapped[float] = mapped_column(Float, nullable=False)
    skills_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    experience_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    semantic_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    education_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    bm25_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    vector_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    hybrid_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    score_breakdown = mapped_column(JSON, nullable=True)
    matched_skills = mapped_column(JSON, nullable=True)
    missing_skills = mapped_column(JSON, nullable=True)
    experience_match: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    job = relationship("Job", back_populates="rankings")
    candidate = relationship("Candidate", back_populates="rankings")

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<RankingResult(job_id={self.job_id}, candidate_id={self.candidate_id}, "
            f"rank={self.rank}, score={self.match_score})>"
        )