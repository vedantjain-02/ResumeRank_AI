import os
import sys
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ranking_service import RankingService, HybridOptions


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def _make_candidate(id=1, name="C", tags=None, years=5, seniority="Senior",
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
        functional_expertise=[{"area": "Backend Development", "years": years}],
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
        description=description or "Hiring a Python backend developer with strong API experience.",
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
# 1. Requested limit is respected
# ----------------------------------------------------------------------

def test_top_5_returns_5_when_at_least_5_suitable_candidates():
    service = RankingService()
    candidates = [_make_candidate(i, f"C{i}") for i in range(1, 21)]
    db = _mock_db(candidates)
    job = _make_job(min_exp=0, seniority="")
    options = HybridOptions(enable_min_experience=False, enable_seniority=False)

    ranked = service.rank_candidates(db, job, top_n=5, options=options)

    assert len(ranked["top_candidates"]) == 5
    assert ranked["pipeline_stats"]["selected_limit"] == 5
    assert ranked["pipeline_stats"]["final_ranked"] == 5


def test_top_10_returns_10_when_at_least_10_suitable_candidates():
    service = RankingService()
    candidates = [_make_candidate(i, f"C{i}") for i in range(1, 31)]
    db = _mock_db(candidates)
    job = _make_job(min_exp=0, seniority="")
    options = HybridOptions(enable_min_experience=False, enable_seniority=False)

    ranked = service.rank_candidates(db, job, top_n=10, options=options)

    assert len(ranked["top_candidates"]) == 10
    assert ranked["pipeline_stats"]["selected_limit"] == 10
    assert ranked["pipeline_stats"]["final_ranked"] == 10


def test_fewer_than_limit_returns_available_count_without_error():
    service = RankingService()
    candidates = [_make_candidate(i, f"C{i}") for i in range(1, 4)]
    db = _mock_db(candidates)
    job = _make_job(min_exp=0, seniority="")
    options = HybridOptions(enable_min_experience=False, enable_seniority=False)

    ranked = service.rank_candidates(db, job, top_n=5, options=options)

    assert ranked["top_candidates"] != []
    assert len(ranked["top_candidates"]) == 3
    assert ranked["pipeline_stats"]["final_ranked"] == 3
    assert sorted(c["candidate_id"] for c in ranked["top_candidates"]) == [1, 2, 3]


def test_no_expansion_when_strict_pool_already_meets_the_limit():
    service = RankingService()
    candidates = [_make_candidate(i, f"C{i}") for i in range(1, 13)]
    db = _mock_db(candidates)
    job = _make_job(mandatory="Python, FastAPI, PostgreSQL", min_exp=0, seniority="")
    options = HybridOptions(enable_min_experience=False, enable_seniority=False)

    ranked = service.rank_candidates(db, job, top_n=5, options=options)
    stats = ranked["pipeline_stats"]

    assert stats["strict_hard_filtered"] == 12
    assert stats["hard_filtered"] == 12
    assert stats["relaxed_candidates"] == 0
    assert stats["relaxation_reason"] is None
    assert len(stats["hard_filter_attempts"]) == 1
    assert len(ranked["top_candidates"]) == 5


# ----------------------------------------------------------------------
# 2. Strict pool smaller than the limit -> progressive expansion
# ----------------------------------------------------------------------

def test_strict_small_pool_expands_to_fill_requested_limit():
    service = RankingService()
    # Only the first two candidates satisfy the mandatory skills; the remaining
    # eight "relaxed" candidates are missing PostgreSQL.
    candidates = (
        [_make_candidate(1, "Strict1", tags=["Python", "FastAPI", "PostgreSQL", "Docker"]),
         _make_candidate(2, "Strict2", tags=["Python", "FastAPI", "PostgreSQL", "Docker"])]
        + [_make_candidate(i, f"Relaxed{i}", tags=["Python", "FastAPI"]) for i in range(3, 11)]
    )
    db = _mock_db(candidates)
    job = _make_job(mandatory="Python, PostgreSQL", min_exp=0, seniority="", education_req="")
    options = HybridOptions(enable_min_experience=False, enable_seniority=False, enable_education=False)

    ranked = service.rank_candidates(db, job, top_n=5, options=options)
    stats = ranked["pipeline_stats"]

    assert stats["selected_limit"] == 5
    assert stats["strict_hard_filtered"] == 2
    assert stats["hard_filtered"] == 2
    assert stats["relaxed_candidates"] >= 3
    assert stats["relaxation_reason"] is not None
    levels = [a["level"] for a in stats["hard_filter_attempts"]]
    assert levels[0] == "strict"
    assert "relaxed_mandatory" in levels

    ids = [c["candidate_id"] for c in ranked["top_candidates"]]
    assert len(ids) == 5
    # Strict candidates keep the first slots, filled by relaxed candidates.
    assert set(ids[:2]) == {1, 2}
    assert len([i for i in ids[2:] if i >= 3]) == 3


def test_mandatory_penalty_still_applied_to_relaxed_fill_in_candidates():
    service = RankingService()
    candidates = (
        [_make_candidate(1, "Strict1", tags=["Python", "FastAPI", "PostgreSQL", "Docker"]),
         _make_candidate(2, "Strict2", tags=["Python", "FastAPI", "PostgreSQL", "Docker"])]
        + [_make_candidate(i, f"Relaxed{i}", tags=["Python", "FastAPI"]) for i in range(3, 9)]
    )
    db = _mock_db(candidates)
    job = _make_job(mandatory="Python, PostgreSQL", min_exp=0, seniority="", education_req="")
    options = HybridOptions(enable_min_experience=False, enable_seniority=False, enable_education=False)

    ranked = service.rank_candidates(db, job, top_n=5, options=options)
    top = ranked["top_candidates"]

    strict_scores = [c["match_score"] for c in top if c["candidate_id"] in {1, 2}]
    relaxed = [c for c in top if c["candidate_id"] not in {1, 2}]

    assert relaxed != []
    for c in relaxed:
        bd = c["score_breakdown"]
        assert bd["mandatory_skills_satisfied"] is False
        assert "postgresql" in bd["missing_mandatory"]
        assert bd["pool_level"] == 1
        # The mandatory penalty keeps relaxed fill-ins below every strict winner.
        assert c["match_score"] < min(strict_scores)


def test_exhaustive_pool_only_relies_on_broadest_level_when_needed():
    service = RankingService()
    candidates = (
        [_make_candidate(1, "Strict1", tags=["Python", "FastAPI", "PostgreSQL", "Docker"]),
         _make_candidate(2, "Strict2", tags=["Python", "FastAPI", "PostgreSQL", "Docker"]),
         _make_candidate(3, "Strict3", tags=["Python", "FastAPI", "PostgreSQL", "Docker"])]
        + [_make_candidate(i, f"Relaxed{i}", tags=["Python", "FastAPI"]) for i in range(4, 18)]
    )
    db = _mock_db(candidates)
    job = _make_job(mandatory="Python, PostgreSQL", min_exp=0, seniority="", education_req="")
    options = HybridOptions(enable_min_experience=False, enable_seniority=False, enable_education=False)

    ranked = service.rank_candidates(db, job, top_n=10, options=options)
    stats = ranked["pipeline_stats"]

    assert len(ranked["top_candidates"]) == 10
    assert stats["strict_hard_filtered"] == 3
    assert stats["relaxed_candidates"] >= 7
    assert {c["candidate_id"] for c in ranked["top_candidates"][:3]} == {1, 2, 3}


# ----------------------------------------------------------------------
# 3. Maximum experience bound is never violated by expansion
# ----------------------------------------------------------------------

def test_maximum_experience_is_never_violated_by_expansion():
    service = RankingService()
    candidates = [
        _make_candidate(1, "Fits", tags=["Python"], years=6, seniority="Senior"),
        _make_candidate(2, "Over1", tags=["Python"], years=9, seniority="Senior"),
        _make_candidate(3, "Over2", tags=["Python"], years=11, seniority="Senior"),
        _make_candidate(4, "Over3", tags=["Python"], years=14, seniority="Senior"),
        _make_candidate(5, "Over4", tags=["Python"], years=15, seniority="Senior"),
    ]
    db = _mock_db(candidates)
    job = _make_job(min_exp=0, seniority="", education_req="",
                    description="Backend engineer with 5-8 years of experience.")
    options = HybridOptions(
        enable_min_experience=False, enable_seniority=False, enable_education=False,
        enable_mandatory_skills=True, enable_max_experience=True,
    )

    ranked = service.rank_candidates(db, job, top_n=5, options=options)

    assert ranked["pipeline_stats"]["maximum_experience"] == 8
    assert ranked["pipeline_stats"]["strict_hard_filtered"] == 1
    # Every expansion level must keep the max-experience bound, so only the
    # single candidate within bounds can ever be returned.
    assert [c["candidate_id"] for c in ranked["top_candidates"]] == [1]


def test_max_experience_violators_never_in_expansion_pool():
    service = RankingService()
    candidates = (
        [_make_candidate(1, "Fits", tags=["Python", "PostgreSQL"], years=5),
         _make_candidate(2, "AlsoFits", tags=["Python", "PostgreSQL"], years=7)]
        + [_make_candidate(i, f"OverExp{i}", tags=["Python", "PostgreSQL"], years=12) for i in range(3, 9)]
    )
    db = _mock_db(candidates)
    job = _make_job(mandatory="Python, PostgreSQL", min_exp=0, seniority="", education_req="",
                    description="Senior role, 4-7 years of experience expected.")
    options = HybridOptions(enable_min_experience=False, enable_seniority=False, enable_education=False,
                            enable_max_experience=True)

    ranked = service.rank_candidates(db, job, top_n=5, options=options)

    assert ranked["pipeline_stats"]["strict_hard_filtered"] == 2
    assert set(c["candidate_id"] for c in ranked["top_candidates"]) <= {1, 2}
    assert ranked["pipeline_stats"]["relaxed_candidates"] == 0


# ----------------------------------------------------------------------
# 4. Stats always carry the limit-shape fields
# ----------------------------------------------------------------------

def test_pipeline_stats_include_limit_shape_fields():
    service = RankingService()
    candidates = [_make_candidate(i, f"C{i}") for i in range(1, 9)]
    db = _mock_db(candidates)
    job = _make_job(min_exp=0, seniority="")
    options = HybridOptions(enable_min_experience=False, enable_seniority=False)

    ranked = service.rank_candidates(db, job, top_n=7, options=options)
    stats = ranked["pipeline_stats"]

    for key in ("total_candidates_evaluated", "selected_limit", "strict_hard_filtered",
                "relaxed_candidates", "hard_filtered", "bm25_retrieved",
                "vector_retrieved", "fused_pool", "final_ranked"):
        assert key in stats, f"missing pipeline stat: {key}"

    assert stats["selected_limit"] == 7
    assert stats["strict_hard_filtered"] == 8
    assert stats["bm25_retrieved"] <= stats["strict_hard_filtered"] + stats["relaxed_candidates"]
    assert stats["fused_pool"] >= stats["final_ranked"]
    assert stats["final_ranked"] <= stats["selected_limit"]