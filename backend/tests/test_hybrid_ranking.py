import os
import sys
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _make_candidate(
    id=1,
    name="C1",
    tags=None,
    years=5,
    seniority="Senior",
    summary=None,
    embedding=None,
    education=None,
    job_title="Backend Developer",
):
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


def _bulk_candidates(n):
    labels = ["Mid-Level", "Senior", "Junior", "Lead", "Senior"]
    res = []
    for i in range(1, n + 1):
        res.append(_make_candidate(
            id=i,
            name=f"Candidate {i}",
            tags=["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"][: (i % 5) + 1],
            years=2 + (i % 10),
            seniority=labels[i % 5],
            summary=f"Candidate {i} backend python API experience.",
        ))
    return res


def _make_job(min_exp=3, seniority="Senior", education_req="Bachelor",
              mandatory="", required="Python, FastAPI, PostgreSQL", preferred="Docker"):
    from app.models.job import Job
    return Job(
        id=1,
        title="Backend Developer",
        description="Hiring a Python backend developer with strong API experience.",
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
# 1. 100 candidates available
# ----------------------------------------------------------------------

def test_all_100_candidates_evaluated():
    from app.services.ranking_service import RankingService, HybridOptions

    service = RankingService()
    candidates = _bulk_candidates(100)
    db = _mock_db(candidates)
    # No-op hard filters so every candidate remains in the pool.
    job = _make_job(min_exp=0, seniority="", mandatory="")
    options = HybridOptions()

    ranked = service.rank_candidates(db, job, top_n=5, options=options)

    assert ranked["total_candidates_evaluated"] == 100
    assert ranked["pipeline_stats"]["hard_filtered"] == 100
    assert ranked["pipeline_stats"]["hard_filter_trimmed"] == 50  # 100 -> 50 via prelim relevance
    assert len(ranked["top_candidates"]) == 5
    assert ranked["pipeline_stats"]["final_ranked"] == 5


# ----------------------------------------------------------------------
# 2. Hard filtering reduces the pool
# ----------------------------------------------------------------------

def test_hard_filter_reduces_pool():
    from app.services.ranking_service import RankingService, HybridOptions

    service = RankingService()
    candidates = _bulk_candidates(20)
    db = _mock_db(candidates)
    job = _make_job(min_exp=6, seniority="Senior", mandatory="Python")
    options = HybridOptions()

    pool = service.hard_filter_candidates(db, job, options)
    assert 0 < len(pool) < len(candidates)

    ranked = service.rank_candidates(db, job, top_n=5, options=options)
    assert ranked["pipeline_stats"]["hard_filtered"] == len(pool)
    # everyone remaining meets the hard requirements
    allowed = {"Mid-Level", "Senior", "Lead"}  # Senior rank 3, tolerance 1
    for c in pool:
        assert (c.total_experience_years or 0) >= 6
        assert c.seniority_level in allowed


# ----------------------------------------------------------------------
# 3. BM25 only ever sees the hard-filtered pool
# ----------------------------------------------------------------------

def test_bm25_only_on_filtered_pool(monkeypatch):
    from app.services.ranking_service import RankingService, HybridOptions

    service = RankingService()
    candidates = _bulk_candidates(25)
    db = _mock_db(candidates)
    job = _make_job(min_exp=6, seniority="Senior", mandatory="Python")
    options = HybridOptions()

    pool_ids = {c.id for c in service.hard_filter_candidates(db, job, options)}
    assert 0 < len(pool_ids) < len(candidates)

    seen = []
    orig = service.bm25_retrieve

    def wrapper(cands, job_, opts, limit=None):
        seen.append([c.id for c in cands])
        return orig(cands, job_, opts, limit=limit)

    monkeypatch.setattr(service, "bm25_retrieve", wrapper)
    service.rank_candidates(db, job, top_n=5, options=options)

    assert seen, "BM25 stage should have executed"
    for pool in seen:
        assert set(pool) == pool_ids


# ----------------------------------------------------------------------
# 4. Vector retrieval only ever sees the hard-filtered pool
# ----------------------------------------------------------------------

def test_vector_only_on_filtered_pool(monkeypatch):
    from app.services.ranking_service import RankingService, HybridOptions

    service = RankingService()
    candidates = _bulk_candidates(25)
    db = _mock_db(candidates)
    job = _make_job(min_exp=6, seniority="Senior", mandatory="Python")
    options = HybridOptions()

    pool_ids = {c.id for c in service.hard_filter_candidates(db, job, options)}
    assert 0 < len(pool_ids) < len(candidates)

    seen = []
    orig = service.vector_retrieve

    def wrapper(db_, cands, jd_emb, opts, limit=None):
        seen.append([c.id for c in cands])
        return orig(db_, cands, jd_emb, opts, limit=limit)

    monkeypatch.setattr(service, "vector_retrieve", wrapper)
    service.rank_candidates(db, job, top_n=5, options=options)

    assert seen, "Vector stage should have executed"
    for pool in seen:
        assert set(pool) == pool_ids


# ----------------------------------------------------------------------
# 5. Final top N returns the expected winners
# ----------------------------------------------------------------------

def test_final_top_5_correct():
    from app.services.ranking_service import RankingService, HybridOptions

    service = RankingService()
    candidates = [
        _make_candidate(1, "Best", ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis", "AWS", "Kafka"],
                        12, "Senior", job_title="Senior Backend Developer"),
        _make_candidate(2, "Good1", ["Python", "FastAPI", "PostgreSQL", "Docker"], 8, "Senior"),
        _make_candidate(3, "Good2", ["Python", "FastAPI", "PostgreSQL", "Docker"], 7, "Senior"),
        _make_candidate(4, "Good3", ["Python", "FastAPI", "PostgreSQL"], 6, "Senior"),
        _make_candidate(5, "Good4", ["Python", "FastAPI", "PostgreSQL"], 6, "Senior"),
    ] + [_make_candidate(i, f"Weak{i}", ["Python"], 2, "Junior") for i in range(6, 11)]

    db = _mock_db(candidates)
    job = _make_job(min_exp=3, seniority="Senior", mandatory="Python")
    options = HybridOptions()

    ranked = service.rank_candidates(db, job, top_n=5, options=options)
    ids = [c["candidate_id"] for c in ranked["top_candidates"]]

    assert len(ids) == 5
    assert set(ids) == {1, 2, 3, 4, 5}
    assert ids[0] == 1  # the strongest candidate wins
    assert ranked["pipeline_stats"]["final_ranked"] == 5


# ----------------------------------------------------------------------
# 6. No candidate outside the fused pool appears in the final ranking
# ----------------------------------------------------------------------

def test_no_candidate_outside_pool_in_final_ranking(monkeypatch):
    from app.services.ranking_service import RankingService, HybridOptions

    service = RankingService()
    candidates = _bulk_candidates(12)
    db = _mock_db(candidates)
    job = _make_job(min_exp=4, seniority="Senior", mandatory="Python")
    options = HybridOptions()

    all_ids = {c.id for c in candidates}
    seen_pools = []
    orig = service.bm25_retrieve

    def wrapper(cands, job_, opts, limit=None):
        seen_pools.append(set(c.id for c in cands))
        return orig(cands, job_, opts, limit=limit)

    monkeypatch.setattr(service, "bm25_retrieve", wrapper)
    ranked = service.rank_candidates(db, job, top_n=6, options=options)

    pool_ids = seen_pools[-1] if seen_pools else all_ids
    assert pool_ids < all_ids  # the hard filter did remove some candidates

    final_ids = {c["candidate_id"] for c in ranked["top_candidates"]}
    assert final_ids
    assert final_ids <= pool_ids
    assert ranked["pipeline_stats"]["fused_pool"] >= len(final_ids)


# ----------------------------------------------------------------------
# 7. Explanations and career summaries are preserved
# ----------------------------------------------------------------------

def test_explanations_and_summaries_preserved():
    from app.services.ranking_service import RankingService, HybridOptions

    service = RankingService()
    candidates = _bulk_candidates(10)
    db = _mock_db(candidates)
    job = _make_job(min_exp=2, seniority="Senior", mandatory="Python")
    options = HybridOptions()

    ranked = service.rank_candidates(db, job, top_n=6, options=options)

    assert len(ranked["top_candidates"]) == 6
    for c in ranked["top_candidates"]:
        assert c["explanation"], "Explanation should always be present"
        assert c["career_summary"], "Career summary should always be present"
        assert c["matched_skills"]
        assert c["match_score"] >= 0


# ----------------------------------------------------------------------
# 8. Persistence continues (RankingResult rows are written)
# ----------------------------------------------------------------------

def test_results_persisted_to_db():
    from app.models.ranking import RankingResult
    from app.services.ranking_service import RankingService, HybridOptions

    service = RankingService()
    candidates = [
        _make_candidate(1, "A", ["Python", "FastAPI", "PostgreSQL", "Docker"], 9, "Senior"),
        _make_candidate(2, "B", ["Python", "FastAPI", "PostgreSQL"], 7, "Senior"),
        _make_candidate(3, "C", ["Python", "FastAPI", "Docker"], 6, "Mid-Level"),
        _make_candidate(4, "D", ["Python", "FastAPI"], 6, "Mid-Level"),
        _make_candidate(5, "E", ["Python"], 2, "Junior"),
    ]
    db = _mock_db(candidates)
    job = _make_job(min_exp=2, seniority="Senior", mandatory="Python")
    options = HybridOptions()

    rank_candidates_top_n = 4
    ranked = service.rank_candidates(db, job, top_n=rank_candidates_top_n, options=options)

    adds = [call.args[0] for call in db.add.call_args_list]
    assert len(adds) == rank_candidates_top_n
    assert all(isinstance(r, RankingResult) for r in adds)
    assert [r.rank for r in adds] == [1, 2, 3, 4]
    assert {r.candidate_id for r in adds} == {c["candidate_id"] for c in ranked["top_candidates"]}
    assert {r.match_score for r in adds} == {c["match_score"] for c in ranked["top_candidates"]}
    assert all(r.job_id == 1 for r in adds)