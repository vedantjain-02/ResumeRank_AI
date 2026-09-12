import os
import sys
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _make_candidate(id=1, name="C", tags=None, years=5, seniority="Senior",
                    education=None, embedding=None, job_title="Backend Developer",
                    summary=None):
    from app.models.candidate import Candidate
    return Candidate(
        id=id,
        name=name,
        phone_number="+91 00000 00000",
        career_summary=summary or f"Candidate {name} resume.",
        total_experience_years=years,
        seniority_level=seniority,
        job_title=job_title,
        functional_expertise=[{"area": "Backend Development", "years": years, "details": "API services"}],
        leadership={"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        education=education or [{"degree": "B.Tech", "field": "Computer Science", "institution": "IIT", "graduation_year": 2018}],
        capability_tags=tags or ["Python", "FastAPI", "PostgreSQL"],
        resume_embedding=embedding,
    )


def _make_job(required="Python, Go, FastAPI", preferred="", min_exp=2, education_req="",
              certs="", mandatory="", seniority=""):
    from app.models.job import Job
    return Job(
        id=1,
        title="Backend Developer",
        description="Hiring a Python backend developer with strong API experience.",
        required_skills=required,
        preferred_skills=preferred,
        minimum_experience=min_exp,
        education_requirement=education_req,
        certifications_required=certs,
        is_mandatory_requirements=mandatory,
        seniority_required=seniority,
    )


def _mock_db(candidates):
    db = MagicMock()
    db.query.return_value.all.return_value = candidates
    return db


# ----------------------------------------------------------------------
# compute_final_score: blend + mandatory gate + configurable weights
# ----------------------------------------------------------------------

def test_compute_final_score_blends_detailed_and_retrieval():
    from app.services.ranking_service import RankingService, HybridOptions

    service = RankingService()
    options = HybridOptions()  # 0.75 detailed / 0.25 hybrid

    r = service.compute_final_score({"match_score": 80, "missing_mandatory": []}, 0.5, options)
    assert r["mandatory_ok"] is True
    # (0.75*80 + 0.25*100*0.5) / 1.0 = 72.5
    assert r["final"] == pytest.approx(72.5)

    top = service.compute_final_score({"match_score": 80, "missing_mandatory": []}, 1.0, options)
    assert top["final"] == pytest.approx(85.0)


def test_mandatory_penalty_and_gate():
    from app.services.ranking_service import RankingService, HybridOptions

    service = RankingService()
    options = HybridOptions()

    satisfier = service.compute_final_score({"match_score": 80, "missing_mandatory": []}, 0.5, options)
    missing = service.compute_final_score({"match_score": 80, "missing_mandatory": ["go"]}, 0.5, options)

    assert satisfier["mandatory_ok"] is True
    assert missing["mandatory_ok"] is False
    # penalty (default 5) per missing mandatory skill
    assert missing["final"] == pytest.approx(satisfier["final"] - 5.0)
    assert satisfier["final"] > missing["final"]


def test_final_score_weights_are_configurable():
    from app.services.ranking_service import RankingService, HybridOptions

    service = RankingService()
    high_retrieval = {"match_score": 50, "missing_mandatory": []}   # strong retrieval (1.0)
    high_detailed = {"match_score": 90, "missing_mandatory": []}    # strong detailed (retrieval 0.0)

    retrieval_heavy = HybridOptions(final_hybrid_weight=0.8, final_detailed_weight=0.2)
    detailed_heavy = HybridOptions(final_hybrid_weight=0.1, final_detailed_weight=0.9)

    r_heavy = service.compute_final_score(high_retrieval, 1.0, retrieval_heavy)["final"]
    d_heavy = service.compute_final_score(high_detailed, 0.0, retrieval_heavy)["final"]
    assert r_heavy > d_heavy  # retrieval dominates

    r_light = service.compute_final_score(high_retrieval, 1.0, detailed_heavy)["final"]
    d_light = service.compute_final_score(high_detailed, 0.0, detailed_heavy)["final"]
    assert d_light > r_light  # detailed dominates


# ----------------------------------------------------------------------
# End-to-end: mandatory gate wins over semantic similarity
# ----------------------------------------------------------------------

def test_missing_mandatory_never_outranks_satisfier_despite_semantic_similarity():
    from app.services.ranking_service import RankingService, HybridOptions

    service = RankingService()

    # Candidate A: semantically perfect (vector & embedding identical to JD)
    # but missing the mandatory skill "Go".
    # Candidate B: satisfies all mandatory skills but is otherwise weak.
    jd_like = [0.1] * 384
    weak = [1.0] + [0.0] * 383  # near-orthogonal to the JD embedding (finite cosine)

    a = _make_candidate(
        id=1, name="High Semantic",
        tags=["Python", "FastAPI", "PostgreSQL", "Docker", "Redis", "AWS", "Kafka"],
        years=6, embedding=jd_like,
    )
    b = _make_candidate(
        id=2, name="Mandatory Satisfier",
        tags=["Python", "Go"], years=6, embedding=weak,
    )

    db = _mock_db([a, b])
    job = _make_job(required="Python, Go, FastAPI", mandatory="Go")
    # Disable the mandatory hard-filter so both reach the final stage, where the
    # mandatory gate + penalty must do their job.
    options = HybridOptions(enable_mandatory_skills=False)

    ranked = service.rank_candidates(db, job, top_n=2, options=options)
    ids = [c["candidate_id"] for c in ranked["top_candidates"]]

    assert ids == [2, 1]  # satisfier first, despite candidate 1's semantic edge

    top_bd = ranked["top_candidates"][0]["score_breakdown"]
    second_bd = ranked["top_candidates"][1]["score_breakdown"]
    assert top_bd["mandatory_skills_satisfied"] is True
    assert second_bd["mandatory_skills_satisfied"] is False
    assert "go" in second_bd["missing_mandatory"]
    # sanity: candidate 1 really had the semantic advantage
    assert second_bd["semantic_score"] > top_bd["semantic_score"]


# ----------------------------------------------------------------------
# End-to-end: final score ordering (blend of retrieval + detailed)
# ----------------------------------------------------------------------

def test_final_ranking_orders_by_combined_score():
    from app.services.ranking_service import RankingService, HybridOptions

    service = RankingService()
    jd_like = [0.1] * 384
    weak = [1.0] + [0.0] * 383  # near-orthogonal to the JD embedding

    # Two identical satisfiers except retrieval: A has strong vector similarity.
    a = _make_candidate(1, "RetrievalStrong", ["Python", "Go", "FastAPI"], 6, embedding=jd_like)
    b = _make_candidate(2, "DetailedEqual", ["Python", "Go", "FastAPI"], 6, embedding=weak)

    db = _mock_db([a, b])
    job = _make_job(required="Python, Go, FastAPI", mandatory="Go")

    ranked = service.rank_candidates(db, job, top_n=2, options=HybridOptions())
    scores = {c["candidate_id"]: c["score_breakdown"] for c in ranked["top_candidates"]}

    # Retrieval-strong candidate has a higher hybrid retrieval score and therefore
    # a higher final score -> ranks first.
    assert scores[1]["vector_similarity_score"] > scores[2]["vector_similarity_score"]
    assert scores[1]["final_score"] > scores[2]["final_score"]
    assert ranked["top_candidates"][0]["candidate_id"] == 1


# ----------------------------------------------------------------------
# End-to-end: score breakdown is complete and present in the response
# ----------------------------------------------------------------------

def test_score_breakdown_contains_all_fields():
    from app.services.ranking_service import RankingService, HybridOptions

    service = RankingService()
    candidates = [
        _make_candidate(1, "A", ["Python", "Go", "FastAPI"], 6),
        _make_candidate(2, "B", ["Python", "Go"], 4),
    ]
    db = _mock_db(candidates)
    job = _make_job(required="Python, Go, FastAPI", mandatory="Go")

    ranked = service.rank_candidates(db, job, top_n=2, options=HybridOptions())

    assert len(ranked["top_candidates"]) == 2
    for cand in ranked["top_candidates"]:
        bd = cand["score_breakdown"]
        for key in [
            "hard_filter_result",
            "bm25_score",
            "vector_similarity_score",
            "hybrid_retrieval_score",
            "skills_score",
            "experience_score",
            "semantic_score",
            "education_score",
            "final_score",
        ]:
            assert key in bd, f"missing score_breakdown key: {key}"
        # every score is a 0..100 percentage (hard_filter_result is a pass marker)
        for numeric_key in [
            "bm25_score", "vector_similarity_score", "hybrid_retrieval_score",
            "skills_score", "experience_score", "semantic_score", "education_score",
            "final_score",
        ]:
            assert 0 <= bd[numeric_key] <= 100
        assert bd["hard_filter_result"] == "pass"
        assert bd["final_score"] == cand["match_score"]