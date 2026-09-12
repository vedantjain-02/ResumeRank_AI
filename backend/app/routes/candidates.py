import logging
import os
import re

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy import Text, func
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.models.candidate import Candidate
from app.schemas.candidate import (
    CandidateDetailResponse,
    CandidateListResponse,
    CandidateResponse,
    CandidateUploadResponse,
)
from app.services.candidate_extractor import candidate_extractor
from app.services.embedding_service import embedding_service
from app.services.resume_parser import ResumeParser
from app.config import settings
from app.utils import ensure_upload_dir, validate_file_extension

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/candidates", tags=["Candidates"])


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _candidate_to_response(c: Candidate) -> CandidateResponse:
    return CandidateResponse(
        id=c.id,
        name=c.name,
        phone_number=c.phone_number,
        career_summary=c.career_summary,
        total_experience_years=c.total_experience_years,
        seniority_level=c.seniority_level,
        job_title=c.job_title,
        functional_expertise=c.functional_expertise or [],
        leadership=c.leadership or {},
        education=c.education or [],
        capability_tags=c.capability_tags or [],
        is_seed=c.is_seed,
        created_at=c.created_at,
    )


def _candidate_to_detail(c: Candidate) -> CandidateDetailResponse:
    base = _candidate_to_response(c)
    return CandidateDetailResponse(
        **base.model_dump(),
        resume_text=c.resume_text,
    )


# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------

@router.get("", response_model=CandidateListResponse)
def list_candidates(
    search: Optional[str] = Query(None, description="Search by name, job title, or capability tags"),
    seniority_level: Optional[str] = Query(None, description="Filter by seniority: Junior, Mid-Level, Senior, Lead, Manager"),
    skill: Optional[str] = Query(None, description="Filter by a capability tag (skill)"),
    min_experience: Optional[float] = Query(None, description="Minimum total experience years"),
    max_experience: Optional[float] = Query(None, description="Maximum total experience years"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Candidate)

    if search:
        term = f"%{search.lower()}%"
        query = query.filter(
            Candidate.name.ilike(term)
            | Candidate.job_title.ilike(term)
            | Candidate.career_summary.ilike(term)
            | func.cast(Candidate.capability_tags, Text).ilike(term)
        )

    if seniority_level:
        query = query.filter(Candidate.seniority_level.ilike(seniority_level))

    if skill:
        query = query.filter(func.cast(Candidate.capability_tags, Text).ilike(f"%{skill}%"))

    if min_experience is not None:
        query = query.filter(Candidate.total_experience_years >= min_experience)

    if max_experience is not None:
        query = query.filter(Candidate.total_experience_years <= max_experience)

    total = query.count()
    candidates = query.order_by(Candidate.id).offset(offset).limit(limit).all()

    return CandidateListResponse(
        total=total,
        candidates=[_candidate_to_response(c) for c in candidates],
    )


@router.post("/upload", response_model=CandidateUploadResponse)
async def upload_candidate_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    if not validate_file_extension(file.filename, settings.ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Supported: {', '.join(settings.ALLOWED_EXTENSIONS)}",
        )

    ensure_upload_dir(settings.UPLOAD_DIR)

    # Save file
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    counter = 1
    name_part, ext = os.path.splitext(file.filename)
    while os.path.exists(file_path):
        file_path = os.path.join(settings.UPLOAD_DIR, f"{name_part}_{counter}{ext}")
        counter += 1

    try:
        contents = await file.read()
        if len(contents) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise HTTPException(status_code=413, detail=f"File too large. Max: {settings.MAX_UPLOAD_SIZE_MB}MB")
        with open(file_path, "wb") as fh:
            fh.write(contents)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error saving upload: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to save uploaded file")

    # 1. Extract resume text
    resume_text = ResumeParser.extract_resume_text(file_path)
    if not resume_text:
        raise HTTPException(status_code=400, detail="Could not extract text from resume")

    # 2. Use Grok (or fallback) to extract structured candidate data
    extraction = await candidate_extractor.extract(resume_text)

    # 3. Generate embedding from career_summary (or full resume text as fallback)
    embedding_text = extraction.career_summary or resume_text[:4000]
    embedding = embedding_service.generate_embedding(embedding_text)

    # 4. Build and persist Candidate
    candidate = Candidate(
        name=extraction.name,
        phone_number=extraction.phone_number,
        career_summary=extraction.career_summary,
        total_experience_years=extraction.total_experience_years,
        seniority_level=extraction.seniority_level,
        job_title=extraction.job_title,
        functional_expertise=[item.model_dump() for item in extraction.functional_expertise],
        leadership=extraction.leadership.model_dump(),
        education=[item.model_dump() for item in extraction.education],
        capability_tags=extraction.capability_tags,
        resume_embedding=embedding,
        resume_text=resume_text,
        resume_file_path=file_path,
        is_seed=False,
    )

    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    logger.info("Uploaded candidate: %s (ID: %d)", candidate.name, candidate.id)

    return CandidateUploadResponse(
        id=candidate.id,
        name=candidate.name,
        message="Resume uploaded and processed successfully",
        career_summary_preview=(candidate.career_summary or "")[:500],
    )


@router.get("/{candidate_id}", response_model=CandidateDetailResponse)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return _candidate_to_detail(candidate)