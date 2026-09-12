import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.job import Job
from app.models.ranking import RankingResult
from app.models.candidate import Candidate
from app.services.ranking_service import HybridOptions, ranking_service
from app.schemas.ranking import (
    RankingRequest,
    RankingResponse,
    RankingResultsResponse,
    RankingCandidateResult,
)
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/jobs", tags=["Ranking"])


@router.post("/{job_id}/rank", response_model=RankingResponse)
def rank_job_candidates(
    job_id: int,
    top_n: Optional[int] = Query(settings.DEFAULT_RANKING_LIMIT, ge=1, le=20),
    hard_filter_limit: Optional[int] = Query(None, ge=1),
    bm25_weight: Optional[float] = Query(None, gt=0.0, le=1.0),
    vector_weight: Optional[float] = Query(None, gt=0.0, le=1.0),
    final_hybrid_weight: Optional[float] = Query(None, gt=0.0, le=1.0),
    final_detailed_weight: Optional[float] = Query(None, gt=0.0, le=1.0),
    ranking_request: Optional[RankingRequest] = None,
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # JSON body wins over query params (kept for backward compatibility with the frontend).
    if ranking_request is not None and ranking_request.top_n:
        top_n = ranking_request.top_n
    if top_n is None:
        top_n = settings.DEFAULT_RANKING_LIMIT
    top_n = max(1, min(20, top_n))

    options = HybridOptions()
    if hard_filter_limit is not None:
        options.hard_filter_limit = max(1, hard_filter_limit)
    if bm25_weight is not None:
        options.bm25_weight = bm25_weight
    if vector_weight is not None:
        options.vector_weight = vector_weight
    if final_hybrid_weight is not None:
        options.final_hybrid_weight = final_hybrid_weight
    if final_detailed_weight is not None:
        options.final_detailed_weight = final_detailed_weight

    try:
        ranking_result = ranking_service.rank_candidates(db, job, top_n, options)
    except Exception as e:
        logger.error(f"Ranking failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ranking failed: {str(e)}")

    return RankingResponse(**ranking_result)


@router.get("/{job_id}/results", response_model=RankingResultsResponse)
def get_job_ranking_results(
    job_id: int,
    limit: int = Query(settings.DEFAULT_RANKING_LIMIT, ge=1, le=50),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    results = (
        db.query(RankingResult)
        .filter(RankingResult.job_id == job_id)
        .order_by(RankingResult.rank.asc())
        .limit(limit)
        .all()
    )

    if not results:
        raise HTTPException(
            status_code=404,
            detail="No ranking results found for this job. Run ranking first.",
        )

    response_results = []
    for r in results:
        candidate = db.query(Candidate).filter(Candidate.id == r.candidate_id).first()
        response_results.append(
            RankingCandidateResult(
                rank=r.rank,
                candidate_id=r.candidate_id,
                candidate_name=candidate.name if candidate else "Unknown",
                match_score=r.match_score,
                matched_skills=r.matched_skills or [],
                missing_skills=r.missing_skills or [],
                experience_match=r.experience_match or "",
                explanation=r.explanation or "",
                career_summary=candidate.career_summary if candidate else None,
                score_breakdown=r.score_breakdown or None,
                resume_id=r.candidate_id,
                skills_score=r.skills_score,
                experience_score=r.experience_score,
                semantic_score=r.semantic_score,
                education_score=r.education_score,
            )
        )

    return RankingResultsResponse(
        job_id=job.id,
        job_title=job.title,
        total_results=len(response_results),
        results=response_results,
    )