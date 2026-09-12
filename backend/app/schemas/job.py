from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class JobCreate(BaseModel):
    title: str
    description: str
    required_skills: Optional[str] = None
    preferred_skills: Optional[str] = None
    minimum_experience: Optional[float] = None
    education_requirement: Optional[str] = None
    responsibilities: Optional[str] = None
    certifications_required: Optional[str] = None
    is_mandatory_requirements: Optional[str] = None


class JobResponse(BaseModel):
    id: int
    title: str
    description: str
    required_skills: Optional[str] = None
    preferred_skills: Optional[str] = None
    minimum_experience: Optional[float] = None
    education_requirement: Optional[str] = None
    responsibilities: Optional[str] = None
    certifications_required: Optional[str] = None
    is_mandatory_requirements: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    total: int
    jobs: List[JobResponse]