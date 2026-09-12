import os
import pathlib
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# The live-DB tests below need the *real* credentials (conftest replaces
# DATABASE_URL with throwaway values by default). Restore them from .env.
_env_file = pathlib.Path(__file__).resolve().parents[1] / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        if _line.startswith("DATABASE_URL="):
            os.environ["DATABASE_URL"] = _line.split("=", 1)[1].strip()

from sqlalchemy.dialects import postgresql

from app.services.ranking_service import (
    RankingService,
    HybridOptions,
    _mandatory_skill_condition,
    _education_level_condition,
)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _make_candidate(id=1, name="C", tags=None, years=5, seniority="Senior",
                    education=None, embedding=None, job_title="Backend Developer"):
    from app.models.candidate import Candidate
    return Candidate(
        id=id,
        name=name,
        phone_number="+91 00000 00000",
        career_summary=f"Resume of {name}.",
        total_experience_years=years,
        seniority_level=seniority,
        job_title=job_title,
        functional_expertise=[{"area": "Backend Development"}],
        leadership={"has_leadership": False},
        education=education or [{"degree": "B.Tech", "field": "Computer Science",
                                "institution": "IIT", "graduation_year": 2018}],
        capability_tags=tags or ["Python", "FastAPI", "PostgreSQL"],
        resume_embedding=embedding,
    )


def _make_job(required="Python", preferred="", min_exp=0, education_req="",
              certs="", mandatory="", seniority=""):
    from app.models.job import Job
    return Job(
        id=1,
        title="Backend Developer",
        description="Hiring a Python backend developer.",
        required_skills=required,
        preferred_skills=preferred,
        minimum_experience=min_exp,
        education_requirement=education_req,
        certifications_required=certs,
        is_mandatory_requirements=mandatory,
        seniority_required=seniority,
    )


def _mock_db(candidates):
    from unittest.mock import MagicMock
    db = MagicMock()
    db.query.return_value.all.return_value = candidates
    return db


def _compile_sql(cond):
    return str(cond.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))


def _db_reachable():
    try:
        from app.database import SessionLocal
        with SessionLocal() as db:
            db.execute(__import__("sqlalchemy", fromlist=["select"]).select(__import__("app.models.candidate", fromlist=["Candidate"]).Candidate.id).limit(1))
        return True
    except Exception:
        return False


HAS_DB = _db_reachable()


# ------------------------------------------------------------------
# 1. SQL structure: mandatory skill condition contains expected operators
# ------------------------------------------------------------------

def test_mandatory_skill_sql_contains_expected_keywords():
    cond = _mandatory_skill_condition("python")
    sql = _compile_sql(cond)
    assert "jsonb_array_elements_text" in sql
    assert "->>" in sql  # functional_expertise area extraction
    assert "lower" in sql


def test_mandatory_skill_sql_references_both_sources():
    cond = _mandatory_skill_condition("python")
    sql = _compile_sql(cond)
    assert "ct" in sql  # capability_tags alias
    assert "fe" in sql  # functional_expertise alias


def test_mandatory_skill_sql_has_correct_skill_value():
    cond = _mandatory_skill_condition("django")
    sql = _compile_sql(cond)
    assert "'django'" in sql


# ------------------------------------------------------------------
# 2. SQL structure: education level condition
# ------------------------------------------------------------------

def test_education_level_sql_master_contains_expected_keywords():
    cond = _education_level_condition(4)  # Master
    sql = _compile_sql(cond)
    assert "jsonb_array_elements" in sql
    assert "->>" in sql  # degree/field extraction
    assert "lower" in sql


def test_education_level_sql_master_includes_keywords():
    cond = _education_level_condition(4)  # Master
    sql = _compile_sql(cond)
    assert "master" in sql
    assert "mba" in sql


def test_education_level_sql_bachelor_includes_bachelor():
    cond = _education_level_condition(3)  # Bachelor
    sql = _compile_sql(cond)
    assert "bachelor" in sql
    assert "b.tech" in sql


def test_education_level_sql_higher_level_aggregates_more_keywords():
    l4 = _education_level_condition(4)
    l3 = _education_level_condition(3)
    sql4 = _compile_sql(l4)
    sql3 = _compile_sql(l3)
    assert len(sql4) < len(sql3)  # higher level has fewer keywords -> shorter SQL


# ------------------------------------------------------------------
# 3. hard_filter_candidates: in-memory fallback (MagicMock DB)
# ------------------------------------------------------------------

def test_hard_filter_fallback_includes_mandatory():
    from app.services.ranking_service import RankingService
    service = RankingService()
    candidates = [
        _make_candidate(1, "A", tags=["Python", "FastAPI", "Go"], years=10, seniority="Senior"),
        _make_candidate(2, "B", tags=["Python", "FastAPI"], years=10, seniority="Senior"),
    ]
    db = _mock_db(candidates)
    job = _make_job(min_exp=0, seniority="", mandatory="Python, Go")
    options = HybridOptions(enable_min_experience=False, enable_seniority=False)
    pool = service.hard_filter_candidates(db, job, options)
    ids = {c.id for c in pool}
    assert ids == {1}


def test_hard_filter_fallback_excludes_missing_mandatory():
    from app.services.ranking_service import RankingService
    service = RankingService()
    candidates = [
        _make_candidate(1, "A", tags=["Python", "FastAPI"], years=10, seniority="Senior"),
        _make_candidate(2, "B", tags=["Go", "Rust"], years=10, seniority="Senior"),
    ]
    db = _mock_db(candidates)
    job = _make_job(min_exp=0, seniority="", mandatory="Python, Go")
    options = HybridOptions(enable_min_experience=False, enable_seniority=False)
    pool = service.hard_filter_candidates(db, job, options)
    # Neither candidate has both Python AND Go
    assert len(pool) == 0


def test_hard_filter_fallback_education_gate():
    from app.services.ranking_service import RankingService
    service = RankingService()
    candidates = [
        _make_candidate(1, "A", education=[{"degree": "B.Tech", "field": "CS"}], years=10, seniority="Senior"),
        _make_candidate(2, "B", education=[{"degree": "Masters", "field": "AI"}], years=10, seniority="Senior"),
    ]
    db = _mock_db(candidates)
    job = _make_job(min_exp=0, seniority="", mandatory="", education_req="Master")
    options = HybridOptions(enable_min_experience=False, enable_seniority=False)
    pool = service.hard_filter_candidates(db, job, options)
    ids = {c.id for c in pool}
    assert ids == {2}


def test_hard_filter_no_conditions_added_when_requirements_empty():
    from app.services.ranking_service import RankingService
    service = RankingService()
    candidates = [_make_candidate(i, f"C{i}") for i in range(10)]
    db = _mock_db(candidates)
    job = _make_job(min_exp=0, seniority="", mandatory="", education_req="")
    options = HybridOptions(enable_min_experience=False, enable_seniority=False,
                            enable_mandatory_skills=False, enable_education=False)
    pool = service.hard_filter_candidates(db, job, options)
    assert len(pool) == len(candidates)


# ------------------------------------------------------------------
# 4. Live DB: missing mandatory candidates are excluded
# ------------------------------------------------------------------

@pytest.mark.skipif(not HAS_DB, reason="live PostgreSQL not reachable")
def test_missing_mandatory_excluded_with_real_db():
    from app.database import SessionLocal
    from app.models.candidate import Candidate
    from app.services.ranking_service import RankingService

    service = RankingService()
    missing = Candidate(
        name="MissingMandTester",
        capability_tags=["Python", "Docker"],
        total_experience_years=10,
        seniority_level="Senior",
        job_title="Dev",
        functional_expertise=[{"area": "Backend"}],
        education=[{"degree": "B.Tech", "field": "CS"}],
    )
    with SessionLocal() as db:
        db.add(missing)
        db.commit()
        candidate_id = missing.id

        job = _make_job(min_exp=0, seniority="", mandatory="Python, Go", education_req="")
        options = HybridOptions(enable_min_experience=False, enable_seniority=False)
        pool = service.hard_filter_candidates(db, job, options)
        pool_ids = {c.id for c in pool}
        assert candidate_id not in pool_ids
        db.delete(missing)
        db.commit()


# ------------------------------------------------------------------
# 5. Live DB: SQL vs in-memory pool consistency
# ------------------------------------------------------------------

@pytest.mark.skipif(not HAS_DB, reason="live PostgreSQL not reachable")
def test_sql_vs_in_memory_pool_consistency_job3():
    from app.database import SessionLocal
    from app.models.candidate import Candidate
    from app.models.job import Job
    from app.services.ranking_service import RankingService

    service = RankingService()
    with SessionLocal() as db:
        candidates = db.query(Candidate).all()
        job = db.get(Job, 3)
        options = HybridOptions()
        sql_ids = {c.id for c in service.hard_filter_candidates(db, job, options)}
        mem_ids = {c.id for c in service._apply_in_memory_filters(candidates, job, options)}
        assert sql_ids == mem_ids


@pytest.mark.skipif(not HAS_DB, reason="live PostgreSQL not reachable")
def test_sql_vs_in_memory_pool_consistency_job2():
    from app.database import SessionLocal
    from app.models.candidate import Candidate
    from app.models.job import Job
    from app.services.ranking_service import RankingService

    service = RankingService()
    with SessionLocal() as db:
        candidates = db.query(Candidate).all()
        job = db.get(Job, 2)
        for opts in [HybridOptions(),
                     HybridOptions(enable_mandatory_skills=False, enable_education=False),
                     HybridOptions(enable_seniority=False, enable_min_experience=False)]:
            sql_ids = {c.id for c in service.hard_filter_candidates(db, job, opts)}
            mem_ids = {c.id for c in service._apply_in_memory_filters(candidates, job, opts)}
            assert sql_ids == mem_ids, f"Mismatch with opts={opts}"


@pytest.mark.skipif(not HAS_DB, reason="live PostgreSQL not reachable")
def test_sql_vs_in_memory_education_master():
    from app.database import SessionLocal
    from app.models.candidate import Candidate
    from app.services.ranking_service import RankingService
    from app.models.job import Job

    service = RankingService()
    with SessionLocal() as db:
        candidates = db.query(Candidate).all()
        job = Job(id=999, title="EduTest", description="needs masters",
                  education_requirement="Master", minimum_experience=0,
                  seniority_required="", is_mandatory_requirements="",
                  required_skills="Python", preferred_skills="",
                  certifications_required="")
        opts = HybridOptions(enable_min_experience=False, enable_seniority=False,
                             enable_mandatory_skills=False, enable_education=True)
        sql_ids = {c.id for c in service.hard_filter_candidates(db, job, opts)}
        mem_ids = {c.id for c in service._apply_in_memory_filters(candidates, job, opts)}
        assert sql_ids == mem_ids
