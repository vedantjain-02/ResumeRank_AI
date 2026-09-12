import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _make_candidate(
    tags=None,
    years=5,
    seniority="Senior",
    job_title="Backend Developer",
    education=None,
    functional_expertise=None,
    leadership=None,
    career_summary="Test summary.",
):
    from app.models.candidate import Candidate
    return Candidate(
        id=1,
        name="Test Candidate",
        phone_number="+91 00000 00000",
        career_summary=career_summary,
        total_experience_years=years,
        seniority_level=seniority,
        job_title=job_title,
        functional_expertise=functional_expertise or [{"area": "Backend Development", "years": years}],
        leadership=leadership or {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        education=education or [{"degree": "B.Tech", "field": "Computer Science", "institution": "IIT", "graduation_year": 2018}],
        capability_tags=tags or ["Python", "FastAPI", "PostgreSQL"],
        resume_embedding=None,
    )


def _make_job(required="Python, FastAPI, PostgreSQL", preferred="Docker, Kubernetes", min_exp=3,
              education_req="Bachelor's degree", certs="", mandatory="", seniority="Senior"):
    from app.models.job import Job
    return Job(
        id=1,
        title="Python Backend Developer",
        description="Hiring a Python backend developer with strong API experience.",
        required_skills=required,
        preferred_skills=preferred,
        minimum_experience=min_exp,
        education_requirement=education_req,
        certifications_required=certs,
        is_mandatory_requirements=mandatory,
        seniority_required=seniority,
    )


def test_perfect_match_scores_expected():
    from app.services.ranking_service import ranking_service

    candidate = _make_candidate(
        tags=["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes"],
        years=6,
        seniority="Senior",
        education=[{"degree": "B.Tech", "field": "Computer Science", "institution": "IIT", "graduation_year": 2018}],
    )
    job = _make_job(required="Python, FastAPI, PostgreSQL", preferred="Docker, Kubernetes", min_exp=3)

    scores = ranking_service.score_candidate(candidate, job)

    assert scores["matched_skills"]
    assert not scores["missing_skills"]
    assert scores["match_score"] >= 60


def test_missing_mandatory_skill_penalty():
    from app.services.ranking_service import ranking_service

    candidate = _make_candidate(tags=["Java", "Spring Boot"], years=5)
    job = _make_job(required="Python, Django, Docker", mandatory="Python, Docker")

    scores = ranking_service.score_candidate(candidate, job)

    assert len(scores["missing_mandatory"]) >= 1
    assert scores["skills_score"] < 50


def test_experience_requirements():
    from app.services.ranking_service import ranking_service

    junior = _make_candidate(tags=["Python", "FastAPI", "PostgreSQL"], years=1, seniority="Junior")
    senior = _make_candidate(tags=["Python", "FastAPI", "PostgreSQL"], years=12, seniority="Senior")
    job = _make_job(required="Python", min_exp=7)

    junior_scores = ranking_service.score_candidate(junior, job)
    senior_scores = ranking_service.score_candidate(senior, job)

    assert senior_scores["experience_score"] > junior_scores["experience_score"]


def test_scores_normalized_0_to_100():
    from app.services.ranking_service import ranking_service

    candidate = _make_candidate(tags=[], years=0, seniority="Junior", education=[])
    job = _make_job(required="Python, FastAPI", min_exp=5)

    scores = ranking_service.score_candidate(candidate, job)
    assert 0 <= scores["match_score"] <= 100


def test_configurable_weights_change_ranking():
    from app.services.ranking_service import ranking_service
    from app.config import settings

    original = settings.SCORING_WEIGHTS.copy()

    candidate_a = _make_candidate(tags=["Python", "FastAPI", "PostgreSQL", "Docker"], years=2, seniority="Mid-Level")
    candidate_b = _make_candidate(tags=["Python", "FastAPI"], years=10, seniority="Senior")
    job = _make_job(required="Python, FastAPI, PostgreSQL", min_exp=3, preferred="Docker")

    settings.SCORING_WEIGHTS = {"skills": 0.60, "experience": 0.15, "semantic": 0.15, "education": 0.10}
    scores_a_skills = ranking_service.score_candidate(candidate_a, job)["match_score"]
    scores_b_skills = ranking_service.score_candidate(candidate_b, job)["match_score"]

    settings.SCORING_WEIGHTS = {"skills": 0.10, "experience": 0.60, "semantic": 0.15, "education": 0.15}
    scores_a_exp = ranking_service.score_candidate(candidate_a, job)["match_score"]
    scores_b_exp = ranking_service.score_candidate(candidate_b, job)["match_score"]

    settings.SCORING_WEIGHTS = original

    # Skills-heavy: candidate A (more skills) should score higher
    assert scores_a_skills > scores_b_skills
    # Experience-heavy: candidate B (more years) should score higher
    assert scores_b_exp > scores_a_exp


def test_seniority_alignment():
    from app.services.ranking_service import ranking_service

    mid = _make_candidate(tags=["Python", "FastAPI", "PostgreSQL"], years=3, seniority="Mid-Level")
    senior = _make_candidate(tags=["Python", "FastAPI", "PostgreSQL"], years=3, seniority="Senior")
    job = _make_job(required="Python, FastAPI", min_exp=3, seniority="Mid-Level")

    mid_scores = ranking_service.score_candidate(mid, job)
    senior_scores = ranking_service.score_candidate(senior, job)

    assert mid_scores["experience_score"] > senior_scores["experience_score"]