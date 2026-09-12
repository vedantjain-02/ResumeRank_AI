import os
import sys
import pytest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _make_candidate(
    id=1, name="C1", tags=None, years=5, seniority="Senior",
    job_title="Backend Developer", education=None, functional_expertise=None,
    leadership=None,
):
    from app.models.candidate import Candidate
    return Candidate(
        id=id, name=name, phone_number="+91 00000 00000",
        career_summary=f"Candidate {name} resume.",
        total_experience_years=years, seniority_level=seniority,
        job_title=job_title,
        functional_expertise=functional_expertise or [{"area": "Backend Development", "years": years}],
        leadership=leadership or {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        education=education or [{"degree": "B.Tech", "field": "Computer Science", "institution": "IIT", "graduation_year": 2018}],
        capability_tags=tags or ["Python", "FastAPI", "PostgreSQL"],
        resume_embedding=None,
    )


def _make_job(seniority="Senior"):
    from app.models.job import Job
    return Job(
        id=1, title="Backend Developer", description="Python backend developer role.",
        required_skills="Python, FastAPI, PostgreSQL", preferred_skills="Docker",
        minimum_experience=2, education_requirement="Bachelor",
        certifications_required="", is_mandatory_requirements="Python",
        seniority_required=seniority,
    )


def test_rank_candidates_returns_top_n():
    from app.services.ranking_service import RankingService

    service = RankingService()
    db = MagicMock()
    job = _make_job()

    candidates = [
        _make_candidate(
            id=i + 1, name=f"Candidate {i + 1}",
            tags=["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"],
            years=3 + (i % 5),
            seniority=["Junior", "Mid-Level", "Senior", "Senior", "Lead"][i % 5],
        )
        for i in range(10)
    ]
    db.query.return_value.all.return_value = candidates

    ranked = service.rank_candidates(db, job, top_n=5)

    assert ranked["total_candidates_evaluated"] == 10
    assert len(ranked["top_candidates"]) == 5


def test_ranking_does_not_use_name():
    from app.services.ranking_service import RankingService

    service = RankingService()
    job = _make_job()

    candidates = [
        _make_candidate(id=1, name="Adam Smith", tags=["Python", "FastAPI", "Docker"],
                       years=5, seniority="Senior", job_title="Backend Developer"),
        _make_candidate(id=2, name="Eve Johnson", tags=["Python", "FastAPI", "Docker"],
                       years=5, seniority="Senior", job_title="Backend Developer"),
    ]
    db = MagicMock()
    db.query.return_value.all.return_value = candidates

    scores = [service.score_candidate(c, job)["match_score"] for c in candidates]
    assert scores[0] == scores[1]


def test_rank_candidates_sorted_descending():
    from app.services.ranking_service import RankingService

    service = RankingService()
    job = _make_job()

    candidates = [
        _make_candidate(id=1, name="Strong",
                       tags=["Python", "FastAPI", "PostgreSQL", "Docker", "Redis", "AWS", "Kafka"],
                       years=10, seniority="Lead", job_title="Senior Backend Developer"),
        _make_candidate(id=2, name="Weak",
                       tags=["Python", "FastAPI"],
                       years=2, seniority="Junior", job_title="Junior Developer"),
        _make_candidate(id=3, name="Mid",
                       tags=["Python", "FastAPI", "Docker"],
                       years=5, seniority="Senior", job_title="Backend Developer"),
    ]
    db = MagicMock()
    db.query.return_value.all.return_value = candidates

    ranked = service.rank_candidates(db, job, top_n=3)
    scores = [c["match_score"] for c in ranked["top_candidates"]]
    assert scores == sorted(scores, reverse=True)


def test_rank_candidates_empty_db():
    from app.services.ranking_service import RankingService
    from app.models.job import Job

    service = RankingService()
    db = MagicMock()
    db.query.return_value.all.return_value = []

    job = _make_job()
    ranked = service.rank_candidates(db, job, top_n=5)
    assert ranked["total_candidates_evaluated"] == 0
    assert ranked["top_candidates"] == []