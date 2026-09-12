from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------- Structured extraction sub-models ----------

class FunctionalExpertiseItem(BaseModel):
    area: str
    details: Optional[str] = None
    years: Optional[float] = None


class LeadershipDetails(BaseModel):
    has_leadership: bool = False
    roles: List[str] = Field(default_factory=list)
    team_size: Optional[int] = None
    responsibilities: List[str] = Field(default_factory=list)


class EducationItem(BaseModel):
    degree: Optional[str] = None
    field: Optional[str] = None
    institution: Optional[str] = None
    graduation_year: Optional[int] = None


# ---------- Grok extraction result (used for validation) ----------

class CandidateExtraction(BaseModel):
    """Validated structure returned by the Grok-based extractor."""

    name: Optional[str] = None
    phone_number: Optional[str] = None
    career_summary: Optional[str] = None
    total_experience_years: Optional[float] = None
    seniority_level: Optional[str] = None
    job_title: Optional[str] = None
    functional_expertise: List[FunctionalExpertiseItem] = Field(default_factory=list)
    leadership: LeadershipDetails = Field(default_factory=LeadershipDetails)
    education: List[EducationItem] = Field(default_factory=list)
    capability_tags: List[str] = Field(default_factory=list)


# ---------- API request / response schemas ----------

class CandidateUploadResponse(BaseModel):
    id: int
    name: Optional[str]
    message: str
    career_summary_preview: str


class CandidateResponse(BaseModel):
    id: int
    name: Optional[str]
    phone_number: Optional[str]
    career_summary: Optional[str]
    total_experience_years: Optional[float]
    seniority_level: Optional[str]
    job_title: Optional[str]
    functional_expertise: List[FunctionalExpertiseItem] = Field(default_factory=list)
    leadership: LeadershipDetails = Field(default_factory=LeadershipDetails)
    education: List[EducationItem] = Field(default_factory=list)
    capability_tags: List[str] = Field(default_factory=list)
    is_seed: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CandidateListResponse(BaseModel):
    total: int
    candidates: List[CandidateResponse]


class CandidateDetailResponse(BaseModel):
    id: int
    name: Optional[str]
    phone_number: Optional[str]
    career_summary: Optional[str]
    total_experience_years: Optional[float]
    seniority_level: Optional[str]
    job_title: Optional[str]
    functional_expertise: List[FunctionalExpertiseItem] = Field(default_factory=list)
    leadership: LeadershipDetails = Field(default_factory=LeadershipDetails)
    education: List[EducationItem] = Field(default_factory=list)
    capability_tags: List[str] = Field(default_factory=list)
    resume_text: Optional[str] = None
    is_seed: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True