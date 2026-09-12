import json
import logging
import re
from typing import Optional

import httpx

from app.config import settings
from app.schemas.candidate import (
    CandidateExtraction,
    EducationItem,
    FunctionalExpertiseItem,
    LeadershipDetails,
)

logger = logging.getLogger(__name__)

_GROK_SYSTEM = (
    "You are an expert HR technical recruiter. "
    "Extract structured candidate information from resumes. "
    "Never fabricate information. If a field is absent, use null."
)

_GROK_USER_TEMPLATE = """\
Extract structured information from this resume text.

Return ONLY a JSON object with these exact keys:
{{
    "name": "string or null",
    "phone_number": "string or null",
    "career_summary": "string or null – complete professional summary",
    "total_experience_years": number or null,
    "seniority_level": "Junior|Mid-Level|Senior|Lead|Manager or null",
    "job_title": "string or null – current or most relevant job title",
    "functional_expertise": [
        {{"area": "string", "details": "string or null", "years": number or null}}
    ],
    "leadership": {{
        "has_leadership": true/false,
        "roles": ["string"],
        "team_size": number or null,
        "responsibilities": ["string"]
    }},
    "education": [
        {{
            "degree": "string or null",
            "field": "string or null",
            "institution": "string or null",
            "graduation_year": number or null
        }}
    ],
    "capability_tags": ["Python", "FastAPI", "PostgreSQL", ...]
}}

Rules:
- capability_tags must be a flat list of specific, searchable skills/technologies.
- Do NOT guess or invent information. If absent, leave null or empty list.
- total_experience_years must be derived from actual work-history dates.
- seniority_level must be inferred from titles and experience.
- functional_expertise areas should reflect the candidate's core technical domains.

Resume Text:
{resume_text}

Return ONLY the JSON object, no other text."""


class CandidateExtractor:
    """Extracts structured candidate data from resume text using Grok Cloud API.

    When Grok is unavailable, falls back to a rule-based extractor that does
    not fabricate information.
    """

    def __init__(self):
        self.api_key = settings.GROK_API_KEY
        self.api_url = settings.GROK_API_URL
        self.model = settings.GROK_MODEL

    async def extract(self, resume_text: str) -> CandidateExtraction:
        if not self.api_key:
            logger.warning("Grok API key not configured – using rule-based extractor.")
            return self._fallback(resume_text)

        prompt = _GROK_USER_TEMPLATE.format(resume_text=resume_text[:6000])

        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                resp = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": _GROK_SYSTEM},
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.05,
                        "max_tokens": 2500,
                    },
                )

                if resp.status_code != 200:
                    logger.error("Grok API error %s: %s", resp.status_code, resp.text[:300])
                    return self._fallback(resume_text)

                data = resp.json()
                content: str = data["choices"][0]["message"]["content"].strip()

                # Strip markdown fences if present
                if content.startswith("```"):
                    content = content.split("\n", 1)[1]
                    if content.endswith("```"):
                        content = content[: -3]
                    content = content.strip()

                raw = json.loads(content)
                return self._validate(raw)

        except json.JSONDecodeError as exc:
            logger.error("Grok response is not valid JSON: %s", exc)
            return self._fallback(resume_text)
        except httpx.TimeoutException:
            logger.error("Grok API request timed out")
            return self._fallback(resume_text)
        except Exception as exc:  # noqa: BLE001
            logger.error("Grok extraction error: %s", exc)
            return self._fallback(resume_text)

    # ------------------------------------------------------------------
    # Validation helper
    # ------------------------------------------------------------------

    @staticmethod
    def _validate(raw: dict) -> CandidateExtraction:
        """Validate Grok output against Pydantic schema, normalising failures."""
        try:
            return CandidateExtraction.model_validate(raw)
        except Exception:  # noqa: BLE001
            logger.warning("Grok output failed validation, attempting manual parse.")
            return CandidateExtraction(
                name=raw.get("name"),
                phone_number=raw.get("phone_number"),
                career_summary=raw.get("career_summary"),
                total_experience_years=raw.get("total_experience_years"),
                seniority_level=raw.get("seniority_level"),
                job_title=raw.get("job_title"),
                functional_expertise=[
                    FunctionalExpertiseItem.model_validate(f) for f in raw.get("functional_expertise", [])
                ],
                leadership=LeadershipDetails(**(raw.get("leadership") or {})),
                education=[
                    EducationItem.model_validate(e) for e in raw.get("education", [])
                ],
                capability_tags=raw.get("capability_tags", []),
            )

    # ------------------------------------------------------------------
    # Rule-based fallback (no fabrication)
    # ------------------------------------------------------------------

    def _fallback(self, resume_text: str) -> CandidateExtraction:
        text = resume_text
        text_lower = text.lower()

        # --- name: first non-trivial line that looks like a name ---
        name: Optional[str] = None
        for line in text.strip().splitlines()[:6]:
            line = line.strip()
            if (
                not line
                or len(line) > 80
                or any(kw in line.lower() for kw in (
                    "email", "phone", "address", "linkedin",
                    "github", "@", "experience", "skills", "education",
                    "summary", "objective", "certifications",
                ))
            ):
                continue
            if len(line.split()) <= 5:
                name = line
                break

        # --- phone ---
        phone_match = re.search(r"(\+?\d[\d\s\-()]{7,20})", text)
        phone_number = phone_match.group(1).strip() if phone_match else None

        # --- seniority level ---
        seniority: Optional[str] = None
        seniority_map = {
            "lead": "Lead",
            "principal": "Lead",
            "manager": "Manager",
            "director": "Manager",
            "senior": "Senior",
            "sr.": "Senior",
            "mid-level": "Mid-Level",
            "mid level": "Mid-Level",
            "junior": "Junior",
            "jr.": "Junior",
        }
        for key, label in seniority_map.items():
            if re.search(r"\b" + re.escape(key), text_lower):
                seniority = label
                break

        # --- job title: first line that looks like a title ---
        job_title: Optional[str] = None
        title_keywords = [
            "developer", "engineer", "scientist", "analyst", "architect",
            "manager", "lead", "consultant", "designer", "devops",
        ]
        for line in text.strip().splitlines()[:8]:
            line_clean = line.strip()
            if any(kw in line_clean.lower() for kw in title_keywords):
                job_title = line_clean[:120]
                break

        # --- total experience: find years mention, or parse dates ---
        total_exp: Optional[float] = None
        exp_match = re.search(r"(\d+[\+]?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:professional\s+)?experience)", text_lower)
        if exp_match:
            num = re.search(r"(\d+)", exp_match.group(1))
            if num:
                total_exp = float(num.group(1))

        if total_exp is None:
            year_pairs = re.findall(r"(\d{4})\s*[-–]\s*(\d{4}|present|current|now)", text_lower)
            years_set: set[int] = set()
            for start, end in year_pairs:
                try:
                    years_set.add(int(start))
                    if end.isdigit():
                        years_set.add(int(end))
                except ValueError:
                    pass
            if years_set:
                total_exp = float(max(years_set) - min(years_set))

        # --- career summary ---
        career_summary: Optional[str] = None
        for header in ("summary", "professional summary", "career summary", "about", "profile", "objective"):
            idx = text_lower.find(header)
            if idx != -1:
                end = text_lower.find("\n\n", idx + len(header))
                if end == -1:
                    end = min(idx + 1000, len(text))
                career_summary = text[idx : end].strip()
                break

        # --- capability tags: skill-like keywords found in the text ---
        known_skills = [
            "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
            "react", "angular", "vue", "node.js", "django", "flask", "fastapi",
            "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
            "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
            "machine learning", "deep learning", "nlp", "data science",
            "sql", "rest", "graphql", "grpc", "git", "ci/cd",
            "jenkins", "linux", "agile", "scrum",
        ]
        capability_tags: list[str] = [
            kw.title() for kw in known_skills if kw in text_lower
        ]

        # --- functional expertise: infer from skill clusters ---
        expertise_map: list[dict] = []
        cluster_keywords = {
            "Backend Development": ["python", "java", "django", "flask", "fastapi", "postgresql", "sql", "rest api"],
            "Frontend Development": ["javascript", "typescript", "react", "angular", "vue", "html", "css"],
            "Data Science": ["pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "machine learning", "statistics"],
            "DevOps": ["docker", "kubernetes", "terraform", "aws", "azure", "jenkins", "ci/cd", "linux"],
            "Machine Learning": ["tensorflow", "pytorch", "deep learning", "nlp", "computer vision"],
            "Cloud & Infrastructure": ["aws", "azure", "gcp", "terraform", "kubernetes", "docker"],
            "Data Engineering": ["sql", "spark", "kafka", "airflow", "etl"],
        }
        for area, keywords in cluster_keywords.items():
            if any(kw in text_lower for kw in keywords):
                expertise_map.append({"area": area, "details": None, "years": total_exp})

        # --- education: look for degree mentions ---
        education_items: list[dict] = []
        edu_pattern = re.compile(
            r"(?:phd|ph\.d|master|m\.?s|m\.?tech|mba|bachelor|b\.?e|b\.?tech|b\.?s|b\.?a|associate|diploma)"
            r"[^.]{0,120}",
            re.IGNORECASE,
        )
        edu_matches = edu_pattern.findall(text)
        for match_str in edu_matches[:3]:
            edu_items = re.split(r"[.;]", match_str)
            for item in edu_items:
                item = item.strip()
                if len(item) > 10:
                    education_items.append({
                        "degree": item[:100],
                        "field": None,
                        "institution": None,
                        "graduation_year": None,
                    })
                    break

        # --- leadership ---
        leadership: dict = {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []}
        leadership_keywords = ["lead", "managed", "managed team", "managed a team", "direct reports", "mentored", "oversaw"]
        for kw in leadership_keywords:
            if kw in text_lower:
                leadership["has_leadership"] = True
                break

        return CandidateExtraction(
            name=name,
            phone_number=phone_number,
            career_summary=career_summary,
            total_experience_years=total_exp,
            seniority_level=seniority,
            job_title=job_title,
            functional_expertise=[FunctionalExpertiseItem(**e) for e in expertise_map],
            leadership=LeadershipDetails(**leadership),
            education=[EducationItem(**e) for e in education_items],
            capability_tags=capability_tags,
        )


candidate_extractor = CandidateExtractor()