import os
import re
import logging
from typing import List, Set

logger = logging.getLogger(__name__)


def ensure_upload_dir(upload_dir: str):
    os.makedirs(upload_dir, exist_ok=True)


def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()


def validate_file_extension(filename: str, allowed: set) -> bool:
    ext = get_file_extension(filename)
    return ext in allowed


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text


def parse_skills_string(skills_str: str) -> List[str]:
    if not skills_str:
        return []
    skills = re.split(r"[,;|\n]+", skills_str)
    return [clean_text(s) for s in skills if clean_text(s)]


def compute_skill_overlap(candidate_skills: List[str], required_skills: List[str]):
    candidate_set = {s.lower().strip() for s in candidate_skills}
    required_set = {s.lower().strip() for s in required_skills}
    matched = [s for s in required_set if s in candidate_set]
    missing = [s for s in required_set if s not in candidate_set]
    return matched, missing


def categorize_experience_level(years: float) -> str:
    if years >= 10:
        return "Exceptional"
    elif years >= 7:
        return "Strong"
    elif years >= 4:
        return "Good"
    elif years >= 2:
        return "Moderate"
    elif years >= 1:
        return "Entry"
    else:
        return "Limited"


def extract_name_from_text(text: str) -> str:
    lines = text.strip().split("\n")
    for line in lines[:5]:
        line = line.strip()
        if not line or len(line) > 100:
            continue
        if any(
            kw in line.lower()
            for kw in ["email", "phone", "address", "linkedin", "github", "@", "experience", "skills", "education", "certifications"]
        ):
            continue
        if len(line.split()) <= 4 and len(line) >= 3:
            return line
    return "Unknown Candidate"