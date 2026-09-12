from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class RankingRequest(BaseModel):
    top_n: int = 5


class RankingCandidateResult(BaseModel):
    rank: int
    candidate_id: int
    candidate_name: str
    match_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    experience_match: str
    explanation: str
    career_summary: Optional[str] = None
    score_breakdown: Optional[dict] = None
    resume_id: int
    skills_score: Optional[float] = None
    experience_score: Optional[float] = None
    semantic_score: Optional[float] = None
    education_score: Optional[float] = None


class RankingResponse(BaseModel):
    job_id: int
    job_title: str
    total_candidates_evaluated: int
    top_candidates: List[RankingCandidateResult]
    pipeline_stats: Optional[dict] = None


class RankingResultsResponse(BaseModel):
    job_id: int
    job_title: str
    total_results: int
    results: List[RankingCandidateResult]