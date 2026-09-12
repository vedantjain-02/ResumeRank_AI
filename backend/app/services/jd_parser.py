import httpx
import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from app.config import settings
from app.utils import clean_text

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------
# Known skills dictionary used for section-aware / fallback extraction.
# Longer terms first so "natural language processing" wins over "nlp".
# ----------------------------------------------------------------------

SKILL_DICTIONARY = [
    # languages / frameworks
    "python", "java", "golang", "go", "rust", "c++", "c#", "javascript",
    "typescript", "react", "angular", "vue.js", "node.js", "express.js",
    "django", "flask", "fastapi", "spring boot", "spring", "laravel", "rails",
    "dotnet", ".net", "graphql", "grpc", "rest api", "restful", "sql", "nosql",
    # data stores / infra
    "postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch",
    "kafka", "rabbitmq", "snowflake", "bigquery", "redshift", "databricks",
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "terraform",
    "jenkins", "github actions", "gitlab ci", "ci/cd", "linux", "airflow",
    "spark", "pyspark", "hadoop", "flink", "dask", "ray",
    # data science / ML / AI
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "data science", "data engineering", "mlops", "llm",
    "generative ai", "pytorch", "tensorflow", "keras", "scikit-learn", "numpy",
    "pandas", "mlflow", "hugging face", "transformers", "langchain", "openai",
    "prompt engineering", "rag", "recurrent neural networks", "cnns",
    # other common
    "git", "html", "css", "sass", "tableau", "power bi", "excel",
    "agile", "scrum", "microservices", "event-driven", "soap", "kinesis",
]

# ----------------------------------------------------------------------
# Section classification
# ----------------------------------------------------------------------

_MANDATORY_TAGS = (
    "required technical", "technical skills", "required skills", "skills required",
    "must have", "must-have", "required qualif", "qualification", "minimum qualif",
    "key skills", "skills and qualif", "skills & qualif", "job requirements",
    "position requirements", "requirements", "essential", "minimum requirements",
    "what you have", "what you bring", "you bring", "you have:", "what we're looking for",
    "experience required", "requirements:", "required experience", "education and experience",
)

_PREFERRED_TAGS = (
    "preferred", "nice to have", "nice-to-have", "good to have", "good-to-have",
    "bonus", "a plus", "would be great", "desired", "plus.", "plus:",
    "bonus points", "not required but",
)

_RESPONSIBILITY_TAGS = (
    "responsibilit", "duties", "what you'll do", "what you will do",
    "what you'll be doing", "what you will be doing", "key accountabilities",
    "your day-to-day", "the impact you", "what we need you to do",
    "role and responsibilities", "the role involves", "you will",
)

_OFFER_TAGS = (
    "we offer", "what we offer", "what we provide", "benefits", "perks",
    "compensation", "salary", "why join", "what you get",
)

_ABOUT_TAGS = (
    "about the role", "about this role", "about the position", "the role",
    "about us", "about the company", "overview", "introduction", "summary",
    "who we are", "the opportunity", "job description", "the team", "about",
    "company description", "our mission", "who you are",
)

_ALL_SECTION_TAGS = _MANDATORY_TAGS + _PREFERRED_TAGS + _RESPONSIBILITY_TAGS + _OFFER_TAGS + _ABOUT_TAGS

_SECTION_HEADER_MAX_LEN = 80

_FREQ_TERMS = ("required", "must", "essential", "proficiency", "proficient",
               "experience with", "expertise", "strong", "solid", "hands-on",
               "skilled in", "deep knowledge", "working knowledge")


def _clean_skill(skill: Any) -> str:
    return clean_text(str(skill)).lower()


def _dedupe(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _match_skills_text(text: str) -> List[str]:
    """Find known skills present in `text` (case-insensitive, word-bounded)."""
    if not text:
        return []
    text_lower = text.lower()
    found = []
    for skill in sorted(SKILL_DICTIONARY, key=len, reverse=True):
        needle = re.escape(skill)
        if " " in skill or "-" in skill[1:-1] or "/" in skill:
            pattern = needle
        else:
            pattern = r"\b" + needle + r"\b"
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(found, key=lambda s: text_lower.find(s))


def _is_section_header(line: str) -> bool:
    """A JD section header: short title-case/all-caps line, or ends with ':'."""
    if not line:
        return False
    low = line.lower()
    if len(line) > _SECTION_HEADER_MAX_LEN:
        return False
    if any(tag in low for tag in _ALL_SECTION_TAGS):
        return True
    if line.endswith(":"):
        return True
    return False


def _split_sections(jd_text: str) -> List[Tuple[str, str]]:
    """Split JD text into (header, body) sections.

    Inline labels like "Required skills: Python, Django" become header
    "Required skills" with body "Python, Django".
    """
    sections: List[Tuple[str, str]] = []
    current_header = ""
    current_body: List[str] = []

    def flush() -> None:
        if current_header or current_body:
            sections.append((current_header, "\n".join(current_body)))

    for raw in jd_text.splitlines():
        line = raw.strip()
        if _is_section_header(line):
            flush()
            if ":" in line:
                head, _, rest = line.partition(":")
                current_header = head.strip()
                current_body = [rest] if rest.strip() else []
            else:
                current_header = line
                current_body = []
        else:
            current_body.append(raw)
    flush()
    return sections


def _classify_section(header: str) -> str:
    h = header.lower()
    if any(tag in h for tag in _PREFERRED_TAGS):
        return "preferred"
    if any(tag in h for tag in _RESPONSIBILITY_TAGS):
        return "responsibilities"
    if any(tag in h for tag in _OFFER_TAGS):
        return "offer"
    if "soft skill" in h or ("soft" in h.split() and "skill" in h.split()):
        return "soft"
    if any(tag in h for tag in _ABOUT_TAGS):
        return "about"
    if any(tag in h for tag in _MANDATORY_TAGS):
        return "required"
    return "general"


def _extract_title(jd_text: str) -> str:
    first_lines = jd_text.strip().split("\n")[:3]
    for raw in first_lines:
        line = clean_text(raw)
        if line and len(line) < 100 and not any(
            kw in line.lower() for kw in ("about", "company", "we are", "looking")
        ):
            return line
    return "Unknown Position"


def _extract_min_experience(text: str) -> float:
    m = re.search(r"(\d+)\+?\s*(?:years?|yrs?)", text.lower())
    return float(m.group(1)) if m else 0


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


def _extract_education(text: str) -> str:
    if not text:
        return "Not specified"
    low = text.lower()
    pattern = re.compile(
        r"(\b(?:bachelor'?s?|master'?s?|ph\.?d\.?|b\.?s\.?c?\.?|m\.?s\.?c?\.?|"
        r"b\.?tech|m\.?tech|associate'?s?|diploma|mba)"
        r"(?:'s)?\s*(?:degree)?\s*(?:in\s+|of\s+)?"
        r"[a-z][a-z /-]{0,30})"
    )
    m = pattern.search(low)
    if not m:
        return "Not specified"
    phrase = clean_text(m.group(1))
    words = phrase.split()
    if words and words[0] in ("bachelor's", "master's", "associate's", "b.s.", "m.s.", "m.b.a."):
        words[0] = words[0][0].upper() + words[0][1:]
    return " ".join(words) or "Not specified"


def _extract_certifications(text: str) -> List[str]:
    cert_keywords = ["certification", "certified", "aws certified", "azure certified",
                     "pmp", "scrum master", "cissp", "cfe", "cfa"]
    certs = []
    low = text.lower()
    for kw in cert_keywords:
        if kw in low:
            certs.append(kw.title())
    return certs


def _select_mandatory(required_skills: List[str], jd_text_lower: str, title: str, max_count: int) -> List[str]:
    """Pick the most important mandatory skills from the required-bucket.

    Ranking signals (in priority order):
      1. explicit required wording ("must", "required", "proficiency", ...)
      2. skill frequency across the whole JD
      3. role relevance (word overlap with the job title)
    """
    title_tokens = set(re.findall(r"[a-z0-9+.#/_-]+", title.lower()))
    scored = []
    for i, skill in enumerate(required_skills):
        freq = jd_text_lower.count(skill)
        explicit = sum(1 for term in _FREQ_TERMS if term in skill)  # skill itself carries the marker
        role = 1.0 if any(tok in skill for tok in title_tokens) else 0.0
        # explicit wording proximity: count lines containing the skill and a
        # "must/required/..." marker (already restricted to required sections by caller)
        explicit_lines = 0
        for chunk in _PRESENTATION_LINES:
            if chunk is None:
                continue
            if skill in chunk and any(term in chunk for term in _FREQ_TERMS):
                explicit_lines += 1
        if explicit_lines > 0:
            explicit += explicit_lines * 2
        score = freq * 1.0 + explicit * 1.5 + role * 2.0
        scored.append((score, -i, skill))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [s for _, _, s in scored[:max_count]]


_PRESENTATION_LINES: List[Optional[str]] = [None]


def parse_skill_structure(jd_text: str, max_mandatory: int = settings.MAX_MANDATORY_SKILLS) -> dict:
    """Section-aware extraction of mandatory / preferred / inferred / required skills.

    Only skills under explicitly required sections are eligible to be mandatory.
    Preferred / responsibilities / offer / soft / about / general sections never
    become mandatory and never shrink the candidate pool.
    """
    sections = _split_sections(jd_text)
    required_bodies: List[str] = []
    preferred_bodies: List[str] = []
    other_bodies: List[str] = []
    for header, body in sections:
        bucket = _classify_section(header)
        if bucket == "required":
            required_bodies.append(body)
        elif bucket == "preferred":
            preferred_bodies.append(body)
        else:
            other_bodies.append(body)

    jd_text_lower = (jd_text or "").lower()
    title = _extract_title(jd_text)

    required_skills = _dedupe(_match_skills_text("\n".join(required_bodies)))
    preferred_skills = _dedupe(_match_skills_text("\n".join(preferred_bodies)))
    other_skills = _dedupe(_match_skills_text("\n".join(other_bodies)))

    # Presentation context for explicit-wording scoring (lines of required sections).
    _PRESENTATION_LINES.clear()
    _PRESENTATION_LINES.extend(line.lower() for chunk in required_bodies for line in chunk.splitlines())

    mandatory = _select_mandatory(required_skills, jd_text_lower, title, max_count=max_mandatory)

    # inferred = mentioned technologies that are neither mandatory nor preferred
    mentioned = _dedupe(_match_skills_text(jd_text))
    known = set(mandatory) | set(preferred_skills)
    inferred = [s for s in mentioned if s not in known]

    # Whatever the cap dropped from the required bucket stays visible as inferred.
    for skill in required_skills:
        if skill not in mandatory and skill not in inferred:
            inferred.append(skill)

    # Preferred bucket: keep only skills that are not already mandatory.
    preferred_skills = [s for s in preferred_skills if s not in mandatory]

    return {
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "inferred_skills": _dedupe(inferred),
        "mandatory_skills": mandatory,
    }


class JDParser:
    def __init__(self):
        self.api_key = settings.GROK_API_KEY
        self.api_url = settings.GROK_API_URL
        self.model = settings.GROK_MODEL
        self.max_mandatory = settings.MAX_MANDATORY_SKILLS

    async def parse_jd(self, jd_text: str) -> Optional[Dict[str, Any]]:
        if not self.api_key:
            logger.warning("Grok API key not configured. Using fallback parser.")
            return self._fallback_parse(jd_text)

        prompt = f"""Analyze this job description and extract structured information as JSON.
Return ONLY a valid JSON object with these exact keys:
{{
    "title": "job title",
    "required_skills": ["skill1", "skill2", ...],
    "preferred_skills": ["skill1", "skill2", ...],
    "minimum_experience": 0.0,
    "education_requirement": "string describing education requirements",
    "responsibilities": "comma-separated list of key responsibilities",
    "certifications_required": ["cert1", "cert2", ...] or [],
    "mandatory_skills": ["skill1", "skill2", ...],
    "inferred_skills": ["skill1", "skill2", ...]
}}

CRITICAL RULES:
- "mandatory_skills" must ONLY contain skills listed under clearly required sections such as
  "Required Technical Skills", "Must Have", or "Required Qualifications".
- NEVER put skills from "About the Role", "Key Responsibilities", "Preferred Skills",
  "Nice to Have", "What We Offer", "Soft Skills", or the general description into mandatory_skills.
- mandatory_skills must be at most 10 skills, ideally 5-8 core skills.
- "preferred_skills" = skills under preferred / nice-to-have sections.
- "inferred_skills" = other technologies mentioned anywhere in the JD that are
  neither mandatory nor preferred.
- "required_skills" = the full list of skills stated as required in the JD.

Job Description:
{jd_text[:6000]}

Return ONLY the JSON object, no other text."""

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are a job description analysis expert. Extract structured data from job descriptions."},
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.1,
                        "max_tokens": 2000,
                    },
                )

                if response.status_code != 200:
                    logger.error(f"Grok API error: {response.status_code} - {response.text}")
                    return self._fallback_parse(jd_text)

                data = response.json()
                content = data["choices"][0]["message"]["content"]

                content = content.strip()
                if content.startswith("```"):
                    content = content.split("\n", 1)[1]
                    if content.endswith("```"):
                        content = content[:-3]
                    content = content.strip()

                parsed = json.loads(content)
                return self._normalize_parsed_jd(parsed, jd_text)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Grok response as JSON: {e}")
            return self._fallback_parse(jd_text)
        except httpx.TimeoutException:
            logger.error("Grok API request timed out")
            return self._fallback_parse(jd_text)
        except Exception as e:
            logger.error(f"Grok API error: {e}")
            return self._fallback_parse(jd_text)

    def _normalize_parsed_jd(self, parsed: dict, original_text: str) -> dict:
        def _as_list(value, default=None):
            if isinstance(value, list):
                return value
            if default is not None:
                return default
            return []

        try:
            min_exp = float(parsed.get("minimum_experience", 0))
        except (TypeError, ValueError):
            min_exp = _extract_min_experience(original_text)

        result = {
            "title": parsed.get("title") or _extract_title(original_text),
            "required_skills": _as_list(parsed.get("required_skills")),
            "preferred_skills": _as_list(parsed.get("preferred_skills")),
            "minimum_experience": min_exp,
            "education_requirement": parsed.get("education_requirement") or "Not specified",
            "responsibilities": parsed.get("responsibilities", ""),
            "certifications_required": _as_list(parsed.get("certifications_required")),
            "mandatory_skills": _as_list(parsed.get("mandatory_skills")),
            "inferred_skills": _as_list(parsed.get("inferred_skills")),
        }
        return self._finalize(result, original_text)

    def _finalize(self, result: dict, jd_text: str) -> dict:
        """Normalize the three skill lists: dedupe, lowercase, and cap mandatory.

        The section-aware fallback is always available as a safety net, so the
        hard filter can never be blocked by an over-eager mandatory list.
        """
        mandatory = _dedupe([_clean_skill(s) for s in result.get("mandatory_skills", []) if _clean_skill(s)])
        preferred = _dedupe([_clean_skill(s) for s in result.get("preferred_skills", []) if _clean_skill(s)])
        required = _dedupe([_clean_skill(s) for s in result.get("required_skills", []) if _clean_skill(s)])
        inferred = _dedupe([_clean_skill(s) for s in result.get("inferred_skills", []) if _clean_skill(s)])

        mandatory = mandatory[: self.max_mandatory]
        known = set(mandatory) | set(preferred) | set(required)
        for skill in _dedupe(_match_skills_text(jd_text)):
            if skill not in known:
                inferred.append(skill)

        result.update(
            required_skills=required,
            preferred_skills=preferred,
            inferred_skills=_dedupe(inferred),
            mandatory_skills=mandatory,
        )
        return result

    def _fallback_parse(self, jd_text: str) -> dict:
        sections = _split_sections(jd_text)
        required_bodies: List[str] = []
        preferred_bodies: List[str] = []
        other_bodies: List[str] = []
        for header, body in sections:
            bucket = _classify_section(header)
            if bucket == "required":
                required_bodies.append(body)
            elif bucket == "preferred":
                preferred_bodies.append(body)
            else:
                other_bodies.append(body)

        required_skills = _dedupe(_match_skills_text("\n".join(required_bodies)))
        preferred_skills = _dedupe(_match_skills_text("\n".join(preferred_bodies)))
        other_skills = _dedupe(_match_skills_text("\n".join(other_bodies)))

        jd_text_lower = (jd_text or "").lower()
        title = _extract_title(jd_text)
        min_exp = _extract_min_experience(jd_text)

        # Education should be read from the required sections first.
        edu_required = _extract_education("\n".join(required_bodies))
        if edu_required == "Not specified":
            edu_required = _extract_education(jd_text)
        education_requirement = edu_required

        certs = _extract_certifications(jd_text)

        _PRESENTATION_LINES.clear()
        _PRESENTATION_LINES.extend(line.lower() for chunk in required_bodies for line in chunk.splitlines())

        mandatory = _select_mandatory(required_skills, jd_text_lower, title, max_count=self.max_mandatory)

        mentioned = _dedupe(_match_skills_text(jd_text))
        known = set(mandatory) | set(preferred_skills)
        inferred = [s for s in mentioned if s not in known]
        for skill in required_skills:
            if skill not in mandatory and skill not in inferred:
                inferred.append(skill)
        for skill in other_skills:
            if skill not in mandatory and skill not in preferred_skills and skill not in inferred:
                inferred.append(skill)

        preferred_skills = [s for s in preferred_skills if s not in mandatory]

        return {
            "title": title,
            "required_skills": required_skills,
            "preferred_skills": preferred_skills,
            "minimum_experience": min_exp,
            "education_requirement": education_requirement,
            "responsibilities": "",
            "certifications_required": certs,
            "mandatory_skills": mandatory,
            "inferred_skills": _dedupe(inferred),
        }