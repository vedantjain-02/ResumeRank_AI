import os
import sys
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ranking_service import RankingService, HybridOptions


def _make_candidate(id=1, name="C1", tags=None, years=5, seniority="Senior",
                    education=None, job_title="Backend Developer"):
    from app.models.candidate import Candidate
    return Candidate(
        id=id,
        name=name,
        phone_number="+91 00000 00000",
        career_summary=f"Candidate {name} resume.",
        total_experience_years=years,
        seniority_level=seniority,
        job_title=job_title,
        functional_expertise=[{"area": "Backend Development"}],
        leadership={"has_leadership": False},
        education=education or [{"degree": "B.Tech", "field": "Computer Science",
                                 "institution": "IIT", "graduation_year": 2018}],
        capability_tags=tags or ["Python", "FastAPI", "PostgreSQL"],
    )


def _make_job(mandatory="", required="Python, FastAPI, PostgreSQL", preferred="",
              min_exp=0, education_req="", seniority="", description=None, title="Backend Developer"):
    from app.models.job import Job
    return Job(
        id=1,
        title=title,
        description=description or "Hiring a Python backend developer with API experience.",
        required_skills=required,
        preferred_skills=preferred,
        minimum_experience=min_exp,
        education_requirement=education_req,
        certifications_required="",
        is_mandatory_requirements=mandatory,
        seniority_required=seniority,
    )


def _mock_db(candidates):
    db = MagicMock()
    db.query.return_value.all.return_value = candidates
    return db


# ----------------------------------------------------------------------
# 1. Relaxed fallback: strict conditions must never yield Top 0
# ----------------------------------------------------------------------

def test_rank_never_returns_empty_when_strict_pool_empty():
    service = RankingService()
    candidates = [_make_candidate(i, f"C{i}", years=4 + i, seniority="Senior") for i in range(1, 8)]
    db = _mock_db(candidates)
    # No candidate has these mandatory skills -> strict pool is empty.
    job = _make_job(mandatory="GoMicroservices, RustCloud, HaskellPlm",
                    min_exp=0, seniority="", education_req="")
    options = HybridOptions(enable_min_experience=False, enable_seniority=False)

    ranked = service.rank_candidates(db, job, top_n=5, options=options)

    assert ranked["total_candidates_evaluated"] == len(candidates)
    assert ranked["pipeline_stats"]["hard_filter_attempts"][0]["level"] == "strict"
    assert ranked["pipeline_stats"]["hard_filter_attempts"][0]["pool_size"] == 0
    assert len(ranked["pipeline_stats"]["hard_filter_attempts"]) > 1
    assert ranked["pipeline_stats"]["relaxation_reason"] is not None
    assert len(ranked["top_candidates"]) == 5


def test_rank_cascades_all_the_way_to_baseline_if_needed():
    service = RankingService()
    # education short-circuits every candidate whose level is below the gate,
    # and mandatory + seniority + experience together eliminate the pool.
    candidates = [
        _make_candidate(1, "Junior", years=1, seniority="Junior",
                        education=[{"degree": "Diploma", "field": "Mechanical"}]),
    ]
    db = _mock_db(candidates)
    job = _make_job(mandatory="QuantumTuring, XChar", min_exp=10,
                    education_req="PhD", seniority="Manager")
    options = HybridOptions()

    ranked = service.rank_candidates(db, job, top_n=5, options=options)
    levels = [a["level"] for a in ranked["pipeline_stats"]["hard_filter_attempts"]]

    assert levels[0] == "strict"
    assert levels[-1] == "baseline"
    assert ranked["top_candidates"] != []
    assert ranked["pipeline_stats"]["final_ranked"] == 1


def test_rank_returns_empty_only_when_no_candidates_exist():
    service = RankingService()
    db = _mock_db([])  # zero candidates
    job = _make_job(mandatory="Python")
    options = HybridOptions()

    ranked = service.rank_candidates(db, job, top_n=5, options=options)
    assert ranked["total_candidates_evaluated"] == 0
    assert ranked["top_candidates"] == []


# ----------------------------------------------------------------------
# 2. Debug statistics for the pipeline
# ----------------------------------------------------------------------

def test_pipeline_stats_debug_keys_present():
    service = RankingService()
    candidates = [_make_candidate(i, f"C{i}") for i in range(1, 5)]
    db = _mock_db(candidates)
    job = _make_job(mandatory="Python, PostgreSQL", preferred="Docker, Redis")

    ranked = service.rank_candidates(db, job, top_n=3)
    stats = ranked["pipeline_stats"]

    assert isinstance(stats["parsed_mandatory_skills"], list)
    assert "python" in stats["parsed_mandatory_skills"]
    assert isinstance(stats["parsed_preferred_skills"], list)
    assert "docker" in stats["parsed_preferred_skills"]
    assert isinstance(stats["parsed_inferred_skills"], list)
    assert isinstance(stats["hard_filter_conditions"], list)
    assert isinstance(stats["hard_filter_attempts"], list)
    assert stats["hard_filter_attempts"] != []
    assert "maximum_experience" in stats
    assert "configuration" in stats
    assert "relaxation_reason" in stats


def test_pipeline_stats_conditions_reflect_mandatory_and_seniority():
    service = RankingService()
    candidates = [_make_candidate(i, f"C{i}", tags=["Python", "FastAPI", "PostgreSQL"]) for i in range(1, 5)]
    db = _mock_db(candidates)
    job = _make_job(mandatory="Python, PostgreSQL", seniority="Senior")
    options = HybridOptions(enable_min_experience=False)

    ranked = service.rank_candidates(db, job, top_n=3, options=options)
    conds = " ".join(ranked["pipeline_stats"]["hard_filter_conditions"])
    assert "mandatory_skill: python" in conds
    assert "mandatory_skill: postgresql" in conds
    assert "seniority" in conds


# ----------------------------------------------------------------------
# 3. Curated / predefined jobs are NOT relaxed (matching pool stays strict)
# ----------------------------------------------------------------------

def test_predefined_job_with_matching_mandatory_stays_strict():
    service = RankingService()
    candidates = [
        _make_candidate(1, "Fit", tags=["Python", "FastAPI", "PostgreSQL", "Docker", "SQL"]),
        _make_candidate(2, "AlsoFit", tags=["Python", "FastAPI", "PostgreSQL", "Docker", "SQL"]),
        _make_candidate(3, "Partial", tags=["Python", "FastAPI"]),
    ]
    db = _mock_db(candidates)
    # Mirrors the curated mandatory list of the seeded "Senior Backend Engineer" job.
    job = _make_job(mandatory="Python, Fastapi, Postgresql, Docker, Sql")

    ranked = service.rank_candidates(db, job, top_n=3)

    assert ranked["pipeline_stats"]["hard_filter_attempts"][0]["level"] == "strict"
    assert ranked["pipeline_stats"]["hard_filter_attempts"][0]["pool_size"] == 2
    assert len(ranked["pipeline_stats"]["hard_filter_attempts"]) == 1
    assert ranked["pipeline_stats"]["relaxation_reason"] is None
    assert ranked["pipeline_stats"]["hard_filtered"] == 2


# ----------------------------------------------------------------------
# 4. Maximum experience upper bound
# ----------------------------------------------------------------------

def test_max_experience_filters_and_is_reported():
    service = RankingService()
    candidates = [
        _make_candidate(1, "A", years=2, seniority="Senior"),
        _make_candidate(2, "B", years=5, seniority="Senior"),
        _make_candidate(3, "C", years=9, seniority="Senior"),
        _make_candidate(4, "D", years=12, seniority="Senior"),
        _make_candidate(5, "E", years=7, seniority="Senior"),
    ]
    db = _mock_db(candidates)
    job = _make_job(min_exp=0, seniority="", description="Backend engineer with 5-8 years of experience.")
    options = HybridOptions(enable_min_experience=False, enable_seniority=False,
                            enable_max_experience=True, enable_mandatory_skills=False,
                            enable_education=False)

    ranked = service.rank_candidates(db, job, top_n=3, options=options)

    assert ranked["pipeline_stats"]["maximum_experience"] == 8
    assert ranked["pipeline_stats"]["hard_filtered"] == 3  # 2, 5, 7 years
    assert ranked["top_candidates"] != []


def test_max_experience_disabled_when_option_off():
    service = RankingService()
    candidates = [
        _make_candidate(1, "A", years=12, seniority="Senior"),
        _make_candidate(2, "B", years=4, seniority="Senior"),
    ]
    db = _mock_db(candidates)
    job = _make_job(min_exp=0, seniority="", description="Engineer with 3-6 years experience.")
    options = HybridOptions(enable_max_experience=False, enable_min_experience=False,
                            enable_seniority=False, enable_mandatory_skills=False,
                            enable_education=False)

    ranked = service.rank_candidates(db, job, top_n=3, options=options)
    assert ranked["pipeline_stats"]["maximum_experience"] is None
    assert ranked["pipeline_stats"]["hard_filtered"] == 2


# ----------------------------------------------------------------------
# 5. Live DB: detailed AI/ML JD must rank non-empty candidates
# ----------------------------------------------------------------------

def test_detailed_ai_ml_jd_returns_ranked_candidates():
    from app.services.jd_parser import parse_skill_structure
    service = RankingService()
    jd_text = """
    Senior AI/ML Engineer
    About the Role:
    You will design and build production ML systems end to end.
    Key Responsibilities:
    - Build training and inference pipelines with FastAPI and Flask.
    - Optimise model serving on Kubernetes.
    Required Technical Skills:
    - Python, PyTorch, TensorFlow, SQL, Snowflake, BigQuery, MLflow, NLP.
    Preferred Skills:
    - Kubernetes, Docker, Terraform, Airflow.
    Education:
    - Master's degree in Computer Science, AI, or a related field preferred.
    """
    structure = parse_skill_structure(jd_text)
    assert "fastapi" not in structure["mandatory_skills"]
    assert "flask" not in structure["mandatory_skills"]

    candidates = [
        _make_candidate(1, "ML1", tags=["Python", "PyTorch", "TensorFlow", "NLP", "SQL"],
                        years=6, seniority="Senior"),
        _make_candidate(2, "ML2", tags=["Python", "SQL", "Snowflake"], years=4, seniority="Senior"),
        _make_candidate(3, "ML3", tags=["Python", "FastAPI"], years=3, seniority="Mid-Level"),
    ]
    db = _mock_db(candidates)
    job = _make_job(
        mandatory=", ".join(structure["mandatory_skills"]),
        required=", ".join(structure["required_skills"]),
        preferred=", ".join(structure["preferred_skills"]),
        description=jd_text,
        title="Senior AI/ML Engineer",
    )
    options = HybridOptions(enable_min_experience=False, enable_seniority=False)

    ranked = service.rank_candidates(db, job, top_n=3, options=options)

    assert ranked["pipeline_stats"]["parsed_mandatory_skills"] == structure["mandatory_skills"]
    assert ranked["top_candidates"] != []
    assert len(ranked["top_candidates"]) >= 1