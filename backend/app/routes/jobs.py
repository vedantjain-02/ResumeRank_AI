import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.job import Job
from app.schemas.job import JobCreate, JobResponse, JobListResponse
from app.services.jd_parser import JDParser

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])

jd_parser = JDParser()


@router.post("", response_model=JobResponse)
async def create_job_with_jd(
    title: Optional[str] = Form(None, description="Job title"),
    description: Optional[str] = Form(None, description="Job description text"),
    file: Optional[UploadFile] = File(None, description="JD file (PDF, DOCX, or TXT)"),
    db: Session = Depends(get_db),
):
    jd_text = None

    if file and file.filename:
        import os
        from app.services.resume_parser import ResumeParser
        from app.config import settings
        from app.utils import validate_file_extension, ensure_upload_dir

        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in {".pdf", ".docx", ".txt", ".md"}:
            raise HTTPException(status_code=400, detail=f"Invalid file type: {ext}")

        ensure_upload_dir(settings.UPLOAD_DIR)
        file_path = os.path.join(settings.UPLOAD_DIR, f"jd_{file.filename}")
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        if ext in {".pdf", ".docx"}:
            jd_text = ResumeParser.extract_resume_text(file_path)
        else:
            jd_text = contents.decode("utf-8", errors="ignore")
    elif description:
        jd_text = description
    else:
        raise HTTPException(status_code=400, detail="Provide job description text or a file")

    if not jd_text or not jd_text.strip():
        raise HTTPException(status_code=400, detail="Job description is empty")

    parsed = await jd_parser.parse_jd(jd_text)

    job = Job(
        title=title or parsed.get("title", "Unknown Position"),
        description=jd_text,
        required_skills=", ".join(parsed.get("required_skills", [])) if isinstance(parsed.get("required_skills"), list) else str(parsed.get("required_skills", "")),
        preferred_skills=", ".join(parsed.get("preferred_skills", [])) if isinstance(parsed.get("preferred_skills"), list) else str(parsed.get("preferred_skills", "")),
        minimum_experience=parsed.get("minimum_experience", 0),
        education_requirement=parsed.get("education_requirement", ""),
        responsibilities=parsed.get("responsibilities", ""),
        certifications_required=", ".join(parsed.get("certifications_required", [])) if isinstance(parsed.get("certifications_required"), list) else str(parsed.get("certifications_required", "")),
        is_mandatory_requirements=", ".join(parsed.get("mandatory_skills", [])) if isinstance(parsed.get("mandatory_skills"), list) else "",
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    logger.info(f"Created job: {job.title} (ID: {job.id})")

    return JobResponse(
        id=job.id,
        title=job.title,
        description=job.description,
        required_skills=job.required_skills,
        preferred_skills=job.preferred_skills,
        minimum_experience=job.minimum_experience,
        education_requirement=job.education_requirement,
        responsibilities=job.responsibilities,
        certifications_required=job.certifications_required,
        is_mandatory_requirements=job.is_mandatory_requirements,
        created_at=job.created_at,
    )


@router.get("", response_model=JobListResponse)
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).order_by(Job.created_at.desc()).all()
    return JobListResponse(
        total=len(jobs),
        jobs=[
            JobResponse(
                id=j.id,
                title=j.title,
                description=j.description,
                required_skills=j.required_skills,
                preferred_skills=j.preferred_skills,
                minimum_experience=j.minimum_experience,
                education_requirement=j.education_requirement,
                responsibilities=j.responsibilities,
                certifications_required=j.certifications_required,
                is_mandatory_requirements=j.is_mandatory_requirements,
                created_at=j.created_at,
            )
            for j in jobs
        ],
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse(
        id=job.id,
        title=job.title,
        description=job.description,
        required_skills=job.required_skills,
        preferred_skills=job.preferred_skills,
        minimum_experience=job.minimum_experience,
        education_requirement=job.education_requirement,
        responsibilities=job.responsibilities,
        certifications_required=job.certifications_required,
        is_mandatory_requirements=job.is_mandatory_requirements,
        created_at=job.created_at,
    )