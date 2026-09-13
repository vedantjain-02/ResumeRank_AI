import logging
import re
from dataclasses import dataclass, field, replace
from typing import Any, Dict, List, Optional

from rank_bm25 import BM25Okapi
from sqlalchemy import func, select, exists, or_
from sqlalchemy.orm import Session

from app.config import settings
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.ranking import RankingResult
from app.services.embedding_service import embedding_service
from app.utils import (
    categorize_experience_level,
    compute_skill_overlap,
    parse_skills_string,
)

logger = logging.getLogger(__name__)

# Seniority hierarchy used for matching
_SENIORITY_RANK = {
    "junior": 1,
    "mid-level": 2,
    "senior": 3,
    "lead": 4,
    "manager": 5,
}

_SENIORITY_LABEL = {
    1: "Junior",
    2: "Mid-Level",
    3: "Senior",
    4: "Lead",
    5: "Manager",
}


# ----------------------------------------------------------------------
# Hybrid retrieval options (configurable per request + env defaults)
# ----------------------------------------------------------------------

@dataclass
class HybridOptions:
    """Configuration for the multi-stage retrieval pipeline (stages 1-4)."""

    hard_filter_limit: int = settings.HARD_FILTER_MAX_POOL_SIZE
    min_pool_target: int = settings.HARD_FILTER_MIN_POOL_SIZE
    bm25_limit: int = settings.BM25_RETRIEVAL_LIMIT
    vector_limit: int = settings.VECTOR_RETRIEVAL_LIMIT
    fusion_limit: int = settings.FUSION_LIMIT
    bm25_weight: float = settings.FUSION_BM25_WEIGHT
    vector_weight: float = settings.FUSION_VECTOR_WEIGHT
    enable_min_experience: bool = settings.HARD_FILTER_MIN_EXPERIENCE
    enable_max_experience: bool = settings.HARD_FILTER_MAX_EXPERIENCE
    maximum_experience: Optional[float] = None
    enable_seniority: bool = settings.HARD_FILTER_SENIORITY
    seniority_tolerance: int = settings.HARD_FILTER_SENIORITY_TOLERANCE
    enable_mandatory_skills: bool = settings.HARD_FILTER_MANDATORY_SKILLS
    enable_education: bool = settings.HARD_FILTER_EDUCATION
    relax_on_empty: bool = settings.HARD_FILTER_RELAX_ON_EMPTY
    max_mandatory_skills: int = settings.MAX_MANDATORY_SKILLS
    # Stage 5 (final combined ranking) configuration
    final_hybrid_weight: float = settings.FINAL_SCORE_HYBRID_WEIGHT
    final_detailed_weight: float = settings.FINAL_SCORE_DETAILED_WEIGHT
    enable_final_hybrid: bool = settings.FINAL_SCORE_ENABLE_HYBRID
    enable_mandatory_priority: bool = settings.FINAL_SCORE_ENABLE_MANDATORY_PRIORITY
    final_mandatory_penalty: float = settings.FINAL_SCORE_MANDATORY_PENALTY
    jd_embedding: Optional[Any] = None


def _extract_capability_tags(candidate: Candidate) -> List[str]:
    """Collect all searchable skill-like strings from the candidate record."""
    tags = list(candidate.capability_tags or [])
    # functional_expertise areas are also searchable skills
    for item in (candidate.functional_expertise or []):
        if isinstance(item, dict):
            area = item.get("area", "")
            if area and area not in tags:
                tags.append(area)
    return tags


_EDU_KEYWORDS = {
    "phd": 5, "ph.d": 5, "doctorate": 5,
    "master": 4, "mba": 4, "m.s": 4, "m.s.": 4, "m.tech": 4, "ma": 4,
    "bachelor": 3, "b.s": 3, "b.s.": 3, "b.tech": 3, "b.e": 3, "ba": 3,
    "associate": 2, "diploma": 1,
}


def _extract_education_level(education_items: List[Any]) -> int:
    """Map education JSONB list to a numeric level (0-5)."""
    best = 0
    for item in education_items:
        text = ""
        if isinstance(item, dict):
            text = f"{item.get('degree', '')} {item.get('field', '')}".lower()
        elif isinstance(item, str):
            text = item.lower()
        for keyword, level in _EDU_KEYWORDS.items():
            if keyword in text:
                best = max(best, level)
    return best


def _seniority_level(seniority_str: Optional[str]) -> int:
    if not seniority_str:
        return 0
    return _SENIORITY_RANK.get(seniority_str.lower().strip(), 0)


def _clean_skills(values) -> List[str]:
    return [str(v).lower().strip() for v in values if str(v).strip()]


def _extract_max_experience(text: str) -> Optional[float]:
    if not text:
        return None
    low = text.lower()
    m = re.search(r"(\d+)\s*(?:-|–|to)\s*(\d+)\s*(?:years?|yrs?)", low)
    if m:
        return float(m.group(2))
    m = re.search(r"up to\s+(\d+)\s*(?:years?|yrs?)", low)
    if m:
        return float(m.group(1))
    return None


# Known-skill list imported lazily to avoid circular imports at module level.
_SKILL_DICT: Optional[List[str]] = None


def _get_skill_dict() -> List[str]:
    global _SKILL_DICT
    if _SKILL_DICT is None:
        from app.services.jd_parser import SKILL_DICTIONARY
        _SKILL_DICT = SKILL_DICTIONARY
    return _SKILL_DICT


def _resolve_skill_structure(job: Job, options: HybridOptions) -> Dict[str, List[str]]:
    """Derive the three skill lists (mandatory/preferred/required) from the
    persisted job fields and compute inferred skills from the description.
    """
    raw_mandatory = _clean_skills(parse_skills_string(job.is_mandatory_requirements or ""))
    raw_preferred = _clean_skills(parse_skills_string(job.preferred_skills or ""))
    raw_required  = _clean_skills(parse_skills_string(job.required_skills or ""))
    mandatory = raw_mandatory[:options.max_mandatory_skills]

    text_lower = (job.description or "").lower()
    known = set(mandatory) | set(raw_preferred) | set(raw_required)
    inferred = [s for s in _get_skill_dict() if s in text_lower and s not in known]
    return {
        "mandatory": mandatory,
        "preferred": raw_preferred,
        "required": raw_required,
        "inferred": inferred,
    }


# ------------------------------------------------------------------
# Hard-filter condition descriptions (for debug output)
# ------------------------------------------------------------------

def _build_hard_filter_conditions(
    job: Job,
    options: HybridOptions,
    mandatory_skills: List[str],
) -> List[str]:
    conds: List[str] = []
    if options.enable_min_experience and (job.minimum_experience or 0) > 0:
        conds.append(f"min_experience_years >= {job.minimum_experience}")
    if options.enable_max_experience and options.maximum_experience:
        conds.append(f"max_experience_years <= {options.maximum_experience}")
    if options.enable_seniority:
        job_rank = _seniority_level(job.seniority_required)
        if job_rank:
            tolerance = max(0, options.seniority_tolerance)
            allowed = sorted(set(range(max(1, job_rank - tolerance),
                                       min(5, job_rank + tolerance) + 1)))
            allowed_labels = [_SENIORITY_LABEL[r] for r in allowed]
            conds.append(f"seniority_level IN {allowed_labels}")
    if options.enable_mandatory_skills:
        for s in mandatory_skills:
            conds.append(f"mandatory_skill: {s}")
    if options.enable_education:
        lvl = _extract_education_level([{"degree": job.education_requirement or ""}])
        if lvl > 0:
            conds.append(f"education_level >= {lvl} ({job.education_requirement})")
    return conds


# ------------------------------------------------------------------
# PostgreSQL JSONB filter conditions (capabilities / education)
# ----------------------------------------------------------------------

def _mandatory_skill_condition(skill: str):
    """SQLAlchemy condition: candidate has `skill` in capability_tags OR
    functional_expertise areas (case-insensitive, exact element match)."""
    cap = func.jsonb_array_elements_text(Candidate.capability_tags).table_valued("tag").render_derived("ct")
    fe = func.jsonb_array_elements(Candidate.functional_expertise).table_valued("doc").render_derived("fe")
    return or_(
        exists(select(1).select_from(cap).where(func.lower(cap.c.tag) == skill)),
        exists(select(1).select_from(fe).where(func.lower(fe.c.doc.op("->>")("area")) == skill)),
    )


def _education_level_condition(min_level: int):
    """SQLAlchemy condition: candidate education level >= min_level.

    Mirrors _extract_education_level (degree + field keyword levels).
    """
    keywords = [kw for kw, lvl in _EDU_KEYWORDS.items() if lvl >= min_level]
    edu = func.jsonb_array_elements(Candidate.education).table_valued("doc").render_derived("edu")
    edu_text = func.lower(func.concat(
        func.coalesce(edu.c.doc.op("->>")("degree"), ""),
        " ",
        func.coalesce(edu.c.doc.op("->>")("field"), ""),
    ))
    return exists(
        select(1).select_from(edu).where(or_(*[edu_text.like(f"%{kw}%") for kw in keywords]))
    )


# ----------------------------------------------------------------------
# Helpers for BM25 / normalization
# ----------------------------------------------------------------------

_TOKEN_RE = re.compile(r"(?u)\b\w[\w+.#-]*\b")


def _tokenize(text: str) -> List[str]:
    if not text:
        return []
    return _TOKEN_RE.findall(text.lower())


def _normalize_scores(mapping: Dict[int, float]) -> Dict[int, float]:
    """Min-max normalize a mapping of candidate_id -> raw score into 0..1."""
    if not mapping:
        return {}
    values = list(mapping.values())
    low, high = min(values), max(values)
    if high - low < 1e-9:
        return {cid: (1.0 if v > 0 else 0.0) for cid, v in mapping.items()}
    return {cid: (v - low) / (high - low) for cid, v in mapping.items()}


class RankingService:
    @property
    def weights(self) -> Dict[str, float]:
        return settings.SCORING_WEIGHTS

    # ------------------------------------------------------------------
    # Core scoring
    # ------------------------------------------------------------------

    def score_candidate(
        self,
        candidate: Candidate,
        job: Job,
        jd_embedding: Optional[Any] = None,
    ) -> Dict[str, Any]:
        candidate_skills = [t.lower().strip() for t in (_extract_capability_tags(candidate))]
        required_skills = [s.lower().strip() for s in parse_skills_string(job.required_skills or "")]
        preferred_skills = [s.lower().strip() for s in parse_skills_string(job.preferred_skills or "")]
        mandatory_skills = [s.lower().strip() for s in parse_skills_string(job.is_mandatory_requirements or "")]
        if not mandatory_skills:
            mandatory_skills = required_skills

        # 1. SKILLS SCORE --------------------------------------------------
        matched_req, missing_req = compute_skill_overlap(candidate_skills, required_skills)
        matched_pref, _ = compute_skill_overlap(candidate_skills, preferred_skills)

        required_ratio = len(matched_req) / len(required_skills) if required_skills else 1.0
        preferred_ratio = len(matched_pref) / len(preferred_skills) if preferred_skills else 0.0

        if required_skills:
            skills_score = (required_ratio * 0.7 + preferred_ratio * 0.3) * 100
        else:
            skills_score = preferred_ratio * 100

        # Job-title alignment bonus (up to +5)
        if candidate.job_title and job.title:
            title_overlap = len(set(candidate.job_title.lower().split()) & set(job.title.lower().split()))
            skills_score = min(100, skills_score + title_overlap * 2.5)

        # Mandatory skill penalty
        missing_mandatory = [s for s in mandatory_skills if s not in candidate_skills]
        if missing_mandatory:
            penalty = settings.MANDATORY_SKILL_PENALTY / max(len(mandatory_skills), 1)
            skills_score *= 1 - penalty * len(missing_mandatory)
            skills_score = max(0, skills_score)

        # 2. EXPERIENCE SCORE -----------------------------------------------
        candidate_exp = candidate.total_experience_years or 0
        required_exp = job.minimum_experience or 0

        if required_exp > 0:
            if candidate_exp >= required_exp:
                exp_ratio = min(candidate_exp / required_exp, 2.0) / 2.0
                experience_score = exp_ratio * 100
            else:
                experience_score = (candidate_exp / required_exp) * 80
        else:
            experience_score = min(100, 50 + candidate_exp * 5)

        # Seniority alignment (adds up to 10 pts if aligned, -5 if mismatch)
        job_seniority = _seniority_level(job.seniority_required)
        cand_seniority = _seniority_level(candidate.seniority_level)
        if job_seniority and cand_seniority:
            gap = abs(job_seniority - cand_seniority)
            if gap == 0:
                experience_score = min(100, experience_score + 10)
            elif gap == 1:
                experience_score = min(100, experience_score + 5)
            else:
                experience_score = max(0, experience_score - 5)

        experience_match = categorize_experience_level(candidate_exp)

        # 3. SEMANTIC SCORE -------------------------------------------------
        semantic_score = 0.0
        if candidate.resume_embedding is not None and job.description:
            if jd_embedding is None:
                jd_embedding = embedding_service.generate_embedding(job.description)
            if jd_embedding:
                semantic_score = (
                    embedding_service.compute_similarity(candidate.resume_embedding, jd_embedding) * 100
                )

        # 4. EDUCATION & CERTIFICATIONS SCORE ------------------------------
        education_score = 50.0  # baseline

        candidate_edu_level = _extract_education_level(candidate.education or [])
        job_edu_level = _extract_education_level([{"degree": job.education_requirement or ""}])

        if job_edu_level > 0:
            if candidate_edu_level >= job_edu_level:
                education_score = 100
            else:
                education_score = max(30, (candidate_edu_level / job_edu_level) * 100)
        else:
            education_score = 70.0

        # Certifications: match capability_tags against job certs
        job_certs = [c.lower().strip() for c in parse_skills_string(job.certifications_required or "")]
        if job_certs:
            matched_certs = [c for c in job_certs if c in candidate_skills]
            cert_ratio = len(matched_certs) / len(job_certs) if job_certs else 1.0
            education_score = education_score * 0.6 + cert_ratio * 100 * 0.4

        # COMBINE ----------------------------------------------------------
        total = (
            skills_score * self.weights["skills"]
            + experience_score * self.weights["experience"]
            + semantic_score * self.weights["semantic"]
            + education_score * self.weights["education"]
        )
        total = max(0, min(100, total))

        return {
            "match_score": round(total, 1),
            "skills_score": round(skills_score, 1),
            "experience_score": round(experience_score, 1),
            "semantic_score": round(semantic_score, 1),
            "education_score": round(education_score, 1),
            "matched_skills": sorted(set(matched_req + matched_pref)),
            "missing_skills": sorted(set(missing_req)),
            "experience_match": experience_match,
            "missing_mandatory": missing_mandatory,
        }

    # ------------------------------------------------------------------
    # Explanation
    # ------------------------------------------------------------------

    def generate_explanation(self, candidate: Candidate, job: Job, scores: dict) -> str:
        parts: list[str] = []
        score = scores["match_score"]

        if score >= 80:
            parts.append(f"Strong match for the {job.title} role")
        elif score >= 60:
            parts.append(f"Good match for the {job.title} role")
        elif score >= 40:
            parts.append(f"Moderate match for the {job.title} role")
        else:
            parts.append(f"Limited match for the {job.title} role")

        matched = scores["matched_skills"]
        if matched:
            parts.append(f"because the candidate has relevant experience in {', '.join(matched[:5])}")

        if scores["missing_skills"]:
            parts.append(f"but is missing {', '.join(scores['missing_skills'][:3])}")

        parts.append(
            f"with {candidate.total_experience_years or 0} years of professional experience "
            f"({candidate.seniority_level or 'unspecified level'})"
        )

        if scores["missing_mandatory"]:
            parts.append(f"Note: missing mandatory skill(s): {', '.join(scores['missing_mandatory'][:3])}")

        return ". ".join(parts) + "."

    # ------------------------------------------------------------------
    # Stage 1: Hard filtering (PostgreSQL-first, configurable)
    # ------------------------------------------------------------------

    def _apply_in_memory_filters(
        self,
        candidates: List[Candidate],
        job: Job,
        options: HybridOptions,
        mandatory_skills: Optional[List[str]] = None,
    ) -> List[Candidate]:
        """In-memory mirror of the hard filters.

        Used when the SQL query layer is unavailable or returns a non-list
        (e.g. MagicMock sessions in unit tests / unusual query drivers), so the
        pipeline is still exercised end-to-end. Semantics match the SQL branch.
        """
        pool = list(candidates or [])

        # --- minimum experience ---
        if options.enable_min_experience and (job.minimum_experience or 0) > 0:
            pool = [c for c in pool if (c.total_experience_years or 0) >= job.minimum_experience]

        # --- maximum experience ---
        if options.enable_max_experience and options.maximum_experience:
            pool = [c for c in pool if (c.total_experience_years or 0) <= options.maximum_experience]

        # --- seniority ---
        if options.enable_seniority:
            job_rank = _seniority_level(job.seniority_required)
            if job_rank:
                tolerance = max(0, options.seniority_tolerance)
                allowed_ranks = set(range(max(1, job_rank - tolerance), min(5, job_rank + tolerance) + 1))
                allowed_labels = [_SENIORITY_LABEL[r] for r in sorted(allowed_ranks)]
                pool = [c for c in pool if (c.seniority_level or "").strip() in allowed_labels]

        # --- mandatory skills (only when the JD explicitly marks them) ---
        if options.enable_mandatory_skills:
            if mandatory_skills is None:
                mandatory_skills = _clean_skills(parse_skills_string(job.is_mandatory_requirements or ""))
            if mandatory_skills:
                kept = []
                for c in pool:
                    tags = {t.lower() for t in _extract_capability_tags(c)}
                    if all(skill in tags for skill in mandatory_skills):
                        kept.append(c)
                pool = kept

        # --- education (only when the JD explicitly requires a degree level) ---
        if options.enable_education:
            job_edu_level = _extract_education_level([{"degree": job.education_requirement or ""}])
            if job_edu_level > 0:
                pool = [c for c in pool if _extract_education_level(c.education or []) >= job_edu_level]

        return pool

    def hard_filter_candidates(
        self,
        db: Session,
        job: Job,
        options: HybridOptions,
        mandatory_skills: Optional[List[str]] = None,
    ) -> List[Candidate]:
        """Filter candidates BEFORE any retrieval.

        - minimum experience: SQL WHERE (scalar column)
        - maximum experience: SQL WHERE (upper bound parsed from JD description)
        - seniority: SQL WHERE (allowed level labels derived from the JD)
        - mandatory skills: only when the JD explicitly marks them (JSONB containment over capability_tags / functional_expertise areas)
        - education: only when the JD explicitly requires a specific level (JSONB degree/field level check)

        Falls back to the in-memory mirror when the query layer cannot produce
        a real list of Candidate rows (e.g. MagicMock sessions in unit tests).

        Protected personal attributes (name, phone, gender, age, religion,
        caste, ...) are never used here.
        """
        conditions = []

        # --- minimum experience (PostgreSQL) ---
        if options.enable_min_experience and (job.minimum_experience or 0) > 0:
            conditions.append(Candidate.total_experience_years >= job.minimum_experience)

        # --- maximum experience (PostgreSQL) ---
        if options.enable_max_experience and options.maximum_experience:
            conditions.append(Candidate.total_experience_years <= options.maximum_experience)

        # --- seniority (PostgreSQL) ---
        if options.enable_seniority:
            job_rank = _seniority_level(job.seniority_required)
            if job_rank:
                tolerance = max(0, options.seniority_tolerance)
                allowed_ranks = set(range(max(1, job_rank - tolerance), min(5, job_rank + tolerance) + 1))
                allowed_labels = [_SENIORITY_LABEL[r] for r in sorted(allowed_ranks)]
                conditions.append(Candidate.seniority_level.in_(allowed_labels))

        # --- mandatory skills (only when the JD explicitly marks them) ---
        if options.enable_mandatory_skills:
            if mandatory_skills is None:
                mandatory_skills = _clean_skills(parse_skills_string(job.is_mandatory_requirements or ""))
            if mandatory_skills:
                conditions.extend(_mandatory_skill_condition(skill) for skill in mandatory_skills)

        # --- education (only when the JD explicitly requires a specific level) ---
        if options.enable_education:
            job_edu_level = _extract_education_level([{"degree": job.education_requirement or ""}])
            if job_edu_level > 0:
                conditions.append(_education_level_condition(job_edu_level))

        pool = None
        try:
            query = db.query(Candidate)
            if conditions:
                query = query.filter(*conditions)
            pool = query.order_by(Candidate.id).all()
        except Exception as exc:  # pragma: no cover - degraded query layers only
            logger.debug("SQL hard-filter query failed, using in-memory path: %s", exc)
            pool = None

        if pool is None or not isinstance(pool, list):
            logger.debug("Hard-filter SQL layer returned a non-list result, using in-memory path.")
            try:
                all_candidates = db.query(Candidate).all()
                if not isinstance(all_candidates, list):
                    all_candidates = list(all_candidates or [])
            except Exception as exc:  # pragma: no cover
                logger.debug("Could not load candidates for in-memory filter: %s", exc)
                all_candidates = []
            pool = self._apply_in_memory_filters(all_candidates, job, options)

        return pool

    # ------------------------------------------------------------------
    # Stage 2: BM25 retrieval (rank-bm25) over the filtered pool
    # ------------------------------------------------------------------

    def build_candidate_document(self, candidate: Candidate) -> str:
        parts: List[str] = []
        if candidate.career_summary:
            parts.append(candidate.career_summary)
        if candidate.job_title:
            parts.append(candidate.job_title)
        for item in (candidate.functional_expertise or []):
            if isinstance(item, dict):
                if item.get("area"):
                    parts.append(str(item["area"]))
                if item.get("details"):
                    parts.append(str(item["details"]))
        parts.extend(str(t) for t in (candidate.capability_tags or []))
        leadership = candidate.leadership or {}
        if isinstance(leadership, dict):
            if leadership.get("has_leadership"):
                parts.append("leadership")
            if leadership.get("roles"):
                parts.append(" ".join(str(r) for r in leadership["roles"]))
            if leadership.get("responsibilities"):
                parts.append(" ".join(str(r) for r in leadership["responsibilities"]))
            if leadership.get("team_size"):
                parts.append(f"team size {leadership['team_size']}")
        for item in (candidate.education or []):
            if isinstance(item, dict):
                parts.extend(
                    str(item.get(k)) for k in ("degree", "field", "institution") if item.get(k)
                )
        return " ".join(p for p in parts if p)

    def build_jd_query(self, job: Job) -> str:
        parts = [
            job.title,
            job.description,
            job.required_skills,
            job.preferred_skills,
            job.responsibilities,
            job.education_requirement,
            job.certifications_required,
            job.is_mandatory_requirements,
        ]
        return " ".join(p for p in parts if p)

    def bm25_retrieve(
        self,
        candidates: List[Candidate],
        job: Job,
        options: HybridOptions,
        limit: Optional[int] = None,
    ) -> Dict[int, float]:
        """BM25 only runs on the (hard-filtered) candidate pool.

        Returns candidate_id -> normalized (0..1) BM25 score for the top `limit`.
        """
        limit = limit or options.bm25_limit
        if not candidates:
            return {}
        corpus = [self.build_candidate_document(c) for c in candidates]
        tokens_corpus = [_tokenize(doc) for doc in corpus]
        query_tokens = _tokenize(self.build_jd_query(job))
        if not query_tokens:
            return {}

        bm25 = BM25Okapi(tokens_corpus)
        raw_scores = bm25.get_scores(query_tokens)

        # BM25 Okapi returns negative scores for documents that only match query
        # terms shared by the whole (small, hard-filtered) corpus. Clamp to 0 so
        # relevance is preserved without dropping candidates.
        mapping = {}
        for i, c in enumerate(candidates):
            mapping[c.id] = max(0.0, float(raw_scores[i]))

        mapped = _normalize_scores(mapping)
        top_ids = sorted(mapping.keys(), key=lambda cid: (mapping[cid], cid), reverse=True)[:limit]
        return {cid: mapped[cid] for cid in top_ids}

    # ------------------------------------------------------------------
    # Stage 3: Vector retrieval (pgvector) over the filtered pool
    # ------------------------------------------------------------------

    def vector_retrieve(
        self,
        db: Session,
        candidates: List[Candidate],
        jd_embedding: Any,
        options: HybridOptions,
        limit: Optional[int] = None,
    ) -> Dict[int, float]:
        """Cosine similarity of the JD embedding vs stored candidate embeddings.

        Uses PostgreSQL pgvector (ORDER BY cosine_distance) restricted to the
        hard-filtered pool. Falls back to in-memory cosine similarity when the
        query layer is unavailable (e.g. unit tests). Candidate embeddings are
        never regenerated - stored resume_embedding vectors are reused.
        """
        limit = limit or options.vector_limit
        if not candidates or jd_embedding is None:
            return {}
        pool_ids = [c.id for c in candidates]

        try:
            dist_expr = Candidate.resume_embedding.cosine_distance(jd_embedding)
            rows = (
                db.query(Candidate.id, dist_expr.label("dist"))
                .filter(
                    Candidate.id.in_(pool_ids),
                    Candidate.resume_embedding.isnot(None),
                )
                .order_by(dist_expr.asc())
                .limit(limit)
                .all()
            )
        except Exception as exc:  # pragma: no cover - non-DB / mocked sessions
            logger.debug("pgvector query unavailable, using in-memory cosine: %s", exc)
            rows = None

        if rows and isinstance(rows, list):
            mapping = {}
            for row in rows:
                try:
                    candidate_id = int(row.id)
                    distance = float(row.dist)
                except (AttributeError, TypeError, ValueError):
                    continue
                similarity = max(0.0, min(1.0, 1.0 - distance))
                if similarity > 0:
                    mapping[candidate_id] = similarity
        else:
            # In-memory fallback restricted to the same filtered pool.
            scores = {}
            for c in candidates:
                if c.resume_embedding is None:
                    continue
                sim = embedding_service.compute_similarity(c.resume_embedding, jd_embedding)
                if sim > 0:
                    scores[c.id] = sim
            top_ids = sorted(scores.keys(), key=lambda cid: (scores[cid], cid), reverse=True)[:limit]
            mapping = {cid: scores[cid] for cid in top_ids}

        normalized = _normalize_scores(mapping)
        return {cid: normalized[cid] for cid in sorted(mapping, key=lambda i: mapping[i], reverse=True)[:limit]}

    # ------------------------------------------------------------------
    # Stage 4: Hybrid score fusion (robust against missing scores)
    # ------------------------------------------------------------------

    def hybrid_score_map(
        self,
        bm25_map: Dict[int, float],
        vector_map: Dict[int, float],
        options: HybridOptions,
    ) -> Dict[int, float]:
        """Weighted hybrid retrieval score (0..1) per candidate.

        Missing BM25 or vector scores for a candidate are handled by
        re-normalizing on the single available score.
        """
        if not bm25_map and not vector_map:
            return {}

        w_bm25 = max(0.0, options.bm25_weight)
        w_vec = max(0.0, options.vector_weight)
        if w_bm25 <= 0 and w_vec <= 0:
            w_bm25, w_vec = 0.5, 0.5

        ids = sorted(set(bm25_map) | set(vector_map))
        fused: Dict[int, float] = {}
        for cid in ids:
            b = bm25_map.get(cid)
            v = vector_map.get(cid)
            if b is None and v is None:
                continue
            if b is not None and v is not None:
                score = (w_bm25 * b + w_vec * v) / (w_bm25 + w_vec)
            elif b is not None:
                score = b  # vector score missing -> rely on BM25
            else:
                score = v  # BM25 score missing -> rely on vector

            fused[cid] = max(0.0, min(1.0, score))

        return fused

    def fuse(
        self,
        bm25_map: Dict[int, float],
        vector_map: Dict[int, float],
        options: HybridOptions,
        limit: Optional[int] = None,
    ) -> List[int]:
        """Weighted fusion of BM25 + vector scores (default 40% / 60%).

        Returns an ordered list of candidate ids (descending relevance), capped
        at `limit`. Per-candidate scores are available via `hybrid_score_map`.
        """
        limit = limit or options.fusion_limit
        fused = self.hybrid_score_map(bm25_map, vector_map, options)

        ordered = sorted(
            fused.keys(),
            key=lambda cid: (fused[cid], vector_map.get(cid, 0.0), bm25_map.get(cid, 0.0), cid),
            reverse=True,
        )
        return ordered[:limit]

    # ------------------------------------------------------------------
    # Stage 5: combined final ranking (hybrid retrieval + detailed score)
    # ------------------------------------------------------------------

    def compute_final_score(
        self,
        detailed: Dict[str, Any],
        retrieval_score: Optional[float],
        options: HybridOptions,
    ) -> Dict[str, Any]:
        """Combine the detailed ranking score (0..100) with the hybrid retrieval
        score (0..1) into the final score (0..100).

        Mandatory skill priority: candidates missing any mandatory skill are
        penalized and (when `enable_mandatory_priority`) are always ranked below
        candidates who satisfy all mandatory skills. The caller enforces the
        ordering gate via `mandatory_ok`.
        """
        detailed_score = float(detailed["match_score"])
        missing = list(detailed.get("missing_mandatory") or [])
        mandatory_ok = len(missing) == 0

        if options.enable_final_hybrid and retrieval_score is not None:
            retrieval_scaled = max(0.0, min(1.0, float(retrieval_score))) * 100.0
        else:
            retrieval_scaled = 0.0

        w_d = max(0.0, options.final_detailed_weight)
        w_r = max(0.0, options.final_hybrid_weight)
        if w_d + w_r <= 0:
            w_d, w_r = 1.0, 0.0

        final_score = (w_d * detailed_score + w_r * retrieval_scaled) / (w_d + w_r)

        if options.enable_mandatory_priority and missing:
            final_score -= options.final_mandatory_penalty * len(missing)

        final_score = max(0.0, min(100.0, final_score))

        return {
            "final": round(final_score, 1),
            "mandatory_ok": mandatory_ok,
            "missing_mandatory": missing,
        }

    # ------------------------------------------------------------------
    # Orchestration: JD -> Hard Filter -> BM25 + pgvector -> Fusion -> Detailed Ranking
    # ------------------------------------------------------------------

    def rank_candidates(
        self,
        db: Session,
        job: Job,
        top_n: int = 5,
        options: Optional[HybridOptions] = None,
    ) -> dict:
        options = options or HybridOptions()
        logger.info("Starting hybrid ranking for job: %s (ID: %d)", job.title, job.id)

        all_candidates = db.query(Candidate).all()
        total = len(all_candidates) if isinstance(all_candidates, (list, tuple)) else 0

        # Resolve the skill structure ONCE and reuse it for hard filtering,
        # staged scoring, and debug output. Derived from the persisted job
        # columns; only explicitly-required skills become mandatory.
        skill_structure = _resolve_skill_structure(job, options)
        mandatory_skills = skill_structure["mandatory"]

        # Maximum experience upper bound, parsed from the JD description
        # (e.g. "5-8 years" -> upper=8). Never set when disabled in config.
        options.maximum_experience = (
            _extract_max_experience(job.description)
            if options.enable_max_experience
            else None
        )

        stats = {
            "total_candidates_evaluated": total,
            "selected_limit": top_n,
            "strict_hard_filtered": 0,
            "relaxed_candidates": 0,
            "hard_filtered": 0,
            "hard_filter_trimmed": 0,
            "bm25_retrieved": 0,
            "vector_retrieved": 0,
            "fused_pool": 0,
            "final_ranked": 0,
            "bm25_weight": options.bm25_weight,
            "vector_weight": options.vector_weight,
            "hard_filter_limit": options.hard_filter_limit,
            "parsed_mandatory_skills": skill_structure["mandatory"],
            "parsed_preferred_skills": skill_structure["preferred"],
            "parsed_inferred_skills": skill_structure["inferred"],
            "maximum_experience": options.maximum_experience,
            "hard_filter_attempts": [],
            "hard_filter_conditions": [],
            "relaxation_reason": None,
            "configuration": {
                "enable_min_experience": options.enable_min_experience,
                "enable_max_experience": options.enable_max_experience,
                "enable_seniority": options.enable_seniority,
                "seniority_tolerance": options.seniority_tolerance,
                "enable_mandatory_skills": options.enable_mandatory_skills,
                "enable_education": options.enable_education,
                "relax_on_empty": options.relax_on_empty,
                "max_mandatory_skills": options.max_mandatory_skills,
            },
        }

        if total == 0:
            logger.info("No candidates to rank.")
            return {
                "job_id": job.id,
                "job_title": job.title,
                "total_candidates_evaluated": 0,
                "top_candidates": [],
                "pipeline_stats": stats,
            }

        # Clear stale rankings for this job
        db.query(RankingResult).filter(RankingResult.job_id == job.id).delete()
        db.commit()

        # JD embedding is computed ONCE and reused by vector retrieval + scoring.
        jd_embedding = embedding_service.generate_embedding(job.description) if job.description else None
        options.jd_embedding = jd_embedding

        # ---- Stage 1: hard filtering with graceful, limit-aware pool expansion ----
        # The requested Top-N must be filled whenever enough candidates exist.
        # The strict hard filter (mandatory skills + seniority + education +
        # experience bounds) yields the highest-confidence candidates. When that
        # pool is smaller than the requested limit we progressively relax the
        # softest conditions and add candidates, keeping every strict candidate
        # first and respecting these rules:
        #   - maximum experience is NEVER relaxed: candidates over the JD's upper
        #     bound only enter the pool if HARD_FILTER_MAX_EXPERIENCE is disabled;
        #   - relaxed fallback candidates still keep the mandatory-priority gate
        #     and the mandatory-skill score penalty;
        #   - the retrieval pool gets enough headroom (>= requested limit, default
        #     40) so BM25 / pgvector / fusion / detailed scoring can fill the
        #     requested Top-N;
        #   - the final limit is applied only after the full pipeline completes.
        strict_pool = self.hard_filter_candidates(db, job, options, mandatory_skills=mandatory_skills)
        attempts = [{
            "level": "strict",
            "pool_size": len(strict_pool),
            "mandatory_skills": len(mandatory_skills),
        }]
        stats["hard_filter_conditions"] = _build_hard_filter_conditions(
            job, options, mandatory_skills,
        )
        relaxation_reason = None

        # Pre-ranking pool target: at least the requested limit, with headroom
        # so the ranking can always be filled (capped by the hard-filter cap).
        pool_target = min(total, max(top_n, options.min_pool_target), options.hard_filter_limit)
        pool = list(strict_pool)
        seen = {c.id for c in strict_pool}
        pool_level: Dict[int, int] = {}
        level_index = 1

        if len(pool) < pool_target:
            expansion_levels = [
                # 1) drop only the mandatory-skill requirement (keep education,
                #    seniority and every experience bound).
                ("relaxed_mandatory", {"enable_mandatory_skills": False}),
                # 2) also drop education (keep seniority and experience bounds).
                ("relaxed_education", {"enable_mandatory_skills": False, "enable_education": False}),
                # 3) also drop seniority (keep the experience bounds).
                ("relaxed_all", {
                    "enable_mandatory_skills": False,
                    "enable_education": False,
                    "enable_seniority": False,
                }),
                # 4) last resort: also drop minimum experience, but ALWAYS keep
                #    the maximum-experience bound.
                ("baseline", {
                    "enable_mandatory_skills": False,
                    "enable_education": False,
                    "enable_seniority": False,
                    "enable_min_experience": False,
                }),
            ]
            for level, overrides in expansion_levels:
                if len(pool) >= pool_target:
                    break
                relaxed_options = replace(options, **overrides)
                candidates_at_level = self.hard_filter_candidates(
                    db, job, relaxed_options, mandatory_skills=[],
                )
                additions = [c for c in candidates_at_level if c.id not in seen]
                room = pool_target - len(pool)
                additions = additions[:room]
                for c in additions:
                    pool_level[c.id] = level_index
                pool.extend(additions)
                seen.update(c.id for c in additions)
                attempts.append({
                    "level": level,
                    "pool_size": len(candidates_at_level),
                    "additions": len(additions),
                })
                if additions and relaxation_reason is None:
                    relaxation_reason = (
                        f"strict filter returned only {len(strict_pool)} candidate(s) "
                        f"for a requested Top-{top_n}; the pool was expanded with "
                        f"{level} candidates to fill the limit."
                    )
                logger.info(
                    "Hard filter '%s': %d seen, +%d added (pool now %d/%d).",
                    level, len(candidates_at_level), len(additions), len(pool), pool_target,
                )
                level_index += 1

        hard_count = len(strict_pool)
        expanded_count = sum(1 for c in pool if pool_level.get(c.id, 0) > 0)
        stats["strict_hard_filtered"] = hard_count
        stats["relaxed_candidates"] = expanded_count
        stats["hard_filtered"] = hard_count
        stats["hard_filter_attempts"] = attempts
        stats["relaxation_reason"] = relaxation_reason
        logger.info(
            "Stage 1 (hard filter): %d strict + %d relaxed = %d candidates in retrieval pool.",
            hard_count, expanded_count, len(pool),
        )

        # If the retrieval pool exceeds `hard_filter_limit` (e.g. a large strict
        # pool), keep the best `hard_filter_limit` candidates using a preliminary
        # relevance score so retrieval + detailed scoring stay bounded.
        if len(pool) > options.hard_filter_limit:
            prelim_bm25 = self.bm25_retrieve(pool, job, options, limit=options.hard_filter_limit)
            prelim_vec = self.vector_retrieve(db, pool, jd_embedding, options, limit=options.hard_filter_limit)
            prelim_ids = set(self.fuse(prelim_bm25, prelim_vec, options, limit=options.hard_filter_limit))
            pre_trim = len(pool)
            pool = [c for c in pool if c.id in prelim_ids]
            stats["hard_filter_trimmed"] = pre_trim - len(pool)
            logger.info(
                "Stage 1 (trim): pool reduced from %d to %d using preliminary relevance.",
                pre_trim, len(pool),
            )

        # ---- Stage 2: BM25 retrieval over the filtered pool ----
        bm25_scores = self.bm25_retrieve(pool, job, options)
        stats["bm25_retrieved"] = len(bm25_scores)
        logger.info("Stage 2 (BM25): retrieved %d candidates.", len(bm25_scores))

        # ---- Stage 3: pgvector retrieval over the filtered pool ----
        vector_scores = self.vector_retrieve(db, pool, jd_embedding, options)
        stats["vector_retrieved"] = len(vector_scores)
        logger.info("Stage 3 (pgvector): retrieved %d candidates.", len(vector_scores))

        # ---- Stage 4: hybrid fusion ----
        fused_ids = self.fuse(bm25_scores, vector_scores, options, limit=options.fusion_limit)
        retrieved = [c for c in pool if c.id in set(fused_ids)]
        stats["fused_pool"] = len(retrieved)
        logger.info("Stage 4 (fusion): %d candidates selected for detailed ranking.", len(retrieved))

        # Per-candidate hybrid retrieval scores (0..1) for the final combine.
        hybrid_map = self.hybrid_score_map(bm25_scores, vector_scores, options)

        # ---- Stage 5: combined final ranking (hybrid retrieval + detailed score) ----
        scored = []
        for cand in retrieved:
            details = self.score_candidate(cand, job, jd_embedding=jd_embedding)
            bm25_n = bm25_scores.get(cand.id, 0.0)
            vec_n = vector_scores.get(cand.id, 0.0)
            hyb = hybrid_map.get(cand.id, 0.0)

            final = self.compute_final_score(details, hyb, options)
            final_score = final["final"]
            mandatory_ok = final["mandatory_ok"]

            details["final_score"] = final_score
            details["bm25_score"] = round(bm25_n * 100, 1)
            details["vector_score"] = round(vec_n * 100, 1)
            details["hybrid_score"] = round(hyb * 100, 1)

            candidate_level = pool_level.get(cand.id, 0)
            breakdown = {
                "hard_filter_result": "pass",
                "pool_level": candidate_level,
                "bm25_score": details["bm25_score"],
                "vector_similarity_score": details["vector_score"],
                "hybrid_retrieval_score": details["hybrid_score"],
                "skills_score": details["skills_score"],
                "experience_score": details["experience_score"],
                "semantic_score": details["semantic_score"],
                "education_score": details["education_score"],
                "final_score": final_score,
                "mandatory_skills_satisfied": mandatory_ok,
                "missing_mandatory": list(details["missing_mandatory"]),
            }
            details["score_breakdown"] = breakdown
            explanation = self.generate_explanation(cand, job, details)

            scored.append({
                "candidate": cand,
                "scores": details,
                "explanation": explanation,
                "breakdown": breakdown,
                "mandatory_ok": mandatory_ok,
                "pool_level": candidate_level,
            })

        # Requirements (kept strict-first):
        #   1) candidates satisfying all mandatory skills ALWAYS outrank
        #      candidates missing a mandatory skill (even with high semantic
        #      similarity) - the mandatory gate plus penalty below;
        #   2) strict hard-filtered candidates always come before relaxed
        #      fallback candidates that were added to fill the requested Top-N;
        #   3) within the same pool level the final score decides the order.
        scored.sort(
            key=lambda x: (
                x.get("pool_level", 0),
                not x["mandatory_ok"],
                -x["scores"]["final_score"],
                x["candidate"].id,
            ),
        )
        top = scored[:top_n]
        stats["final_ranked"] = len(top)
        logger.info("Stage 5 (final): top %d candidates finalized from a pool of %d.", len(top), len(scored))

        # Collect the hybrid score settings for visibility in pipeline_stats.
        stats["final_hybrid_weight"] = options.final_hybrid_weight
        stats["final_detailed_weight"] = options.final_detailed_weight
        stats["enable_final_hybrid"] = options.enable_final_hybrid
        stats["enable_mandatory_priority"] = options.enable_mandatory_priority

        results: list[dict] = []
        for idx, item in enumerate(top, start=1):
            cand = item["candidate"]
            sc = item["scores"]

            db.add(RankingResult(
                job_id=job.id,
                candidate_id=cand.id,
                rank=idx,
                match_score=sc["final_score"],
                skills_score=sc["skills_score"],
                experience_score=sc["experience_score"],
                semantic_score=sc["semantic_score"],
                education_score=sc["education_score"],
                bm25_score=sc["bm25_score"],
                vector_score=sc["vector_score"],
                hybrid_score=sc["hybrid_score"],
                score_breakdown=item["breakdown"],
                matched_skills=sc["matched_skills"],
                missing_skills=sc["missing_skills"],
                experience_match=sc["experience_match"],
                explanation=item["explanation"],
            ))

            results.append({
                "rank": idx,
                "candidate_id": cand.id,
                "candidate_name": cand.name,
                "match_score": sc["final_score"],
                "matched_skills": sc["matched_skills"],
                "missing_skills": sc["missing_skills"],
                "experience_match": sc["experience_match"],
                "explanation": item["explanation"],
                "score_breakdown": item["breakdown"],
                "career_summary": cand.career_summary,
                "resume_id": cand.id,
                "skills_score": sc["skills_score"],
                "experience_score": sc["experience_score"],
                "semantic_score": sc["semantic_score"],
                "education_score": sc["education_score"],
            })

        db.commit()
        logger.info("Ranking complete – stored %d results.", len(results))

        return {
            "job_id": job.id,
            "job_title": job.title,
            "total_candidates_evaluated": total,
            "top_candidates": results,
            "pipeline_stats": stats,
        }


ranking_service = RankingService()