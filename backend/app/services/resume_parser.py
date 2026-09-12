import re
import fitz
import docx
import os
import logging
from typing import Optional
from app.utils import clean_text, get_file_extension

logger = logging.getLogger(__name__)


class ResumeParser:
    @staticmethod
    def _clean_lines(text: str) -> str:
        """Normalize whitespace but preserve line structure for rule-based
        extraction (name/title/section parsing relies on line breaks)."""
        lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.splitlines()]
        cleaned: list[str] = []
        blank = False
        for ln in lines:
            if not ln:
                if blank:
                    continue
                blank = True
                cleaned.append("")
            else:
                blank = False
                cleaned.append(ln)
        while cleaned and cleaned[0] == "":
            cleaned.pop(0)
        while cleaned and cleaned[-1] == "":
            cleaned.pop()
        return "\n".join(cleaned)

    @staticmethod
    def extract_from_pdf(file_path: str) -> Optional[str]:
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return ResumeParser._clean_lines(text)
        except Exception as e:
            logger.error(f"Error extracting PDF {file_path}: {e}")
            return None

    @staticmethod
    def extract_from_docx(file_path: str) -> Optional[str]:
        try:
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return ResumeParser._clean_lines(text)
        except Exception as e:
            logger.error(f"Error extracting DOCX {file_path}: {e}")
            return None

    @classmethod
    def extract_resume_text(cls, file_path: str) -> Optional[str]:
        ext = get_file_extension(file_path)
        if ext == ".pdf":
            return cls.extract_from_pdf(file_path)
        elif ext == ".docx":
            return cls.extract_from_docx(file_path)
        else:
            logger.warning(f"Unsupported file extension: {ext}")
            return None

    @staticmethod
    def extract_candidate_info(resume_text: str) -> dict:
        info = {
            "skills": "",
            "years_of_experience": 0.0,
            "education": "",
            "certifications": "",
            "work_experience": "",
        }

        text_lower = resume_text.lower()

        # Extract skills
        skills_section = ""
        for header in ["skills", "technical skills", "core competencies", "technologies"]:
            pattern = rf"(?:^|\n).*{header}[:\s]*(.*?)(?:\n\s*\n|\n(?=experience|education|certifications|work|summary))"
            match = re.search(pattern, text_lower, re.DOTALL)
            if match:
                skills_section = match.group(1).strip()
                break
        if not skills_section:
            for header in ["skills", "technical skills", "core competencies", "technologies"]:
                idx = text_lower.find(header)
                if idx != -1:
                    end = text_lower.find("\n\n", idx + len(header))
                    if end == -1:
                        end = min(idx + 1000, len(text_lower))
                    skills_section = text_lower[idx + len(header):end].strip()
                    break
        if skills_section:
            info["skills"] = clean_text(skills_section)

        # Extract experience
        exp_match = re.search(r"(\d+[\+]?\s*(?:years?|yrs?)\s*(?:of\s+)?experience)", text_lower)
        if exp_match:
            num_match = re.search(r"(\d+)", exp_match.group(1))
            if num_match:
                info["years_of_experience"] = float(num_match.group(1))

        if info["years_of_experience"] == 0:
            work_section = ""
            for header in ["experience", "work experience", "professional experience", "employment"]:
                idx = text_lower.find(header)
                if idx != -1:
                    end = text_lower.find("\n\n", idx + len(header))
                    if end == -1:
                        end = min(idx + 1500, len(text_lower))
                    work_section = text_lower[idx + len(header):end]
                    break
            if work_section:
                date_ranges = re.findall(r"(\d{4})\s*[-–]\s*(\d{4}|present|current|now)", work_section)
                if date_ranges:
                    years = set()
                    for start, end in date_ranges:
                        try:
                            years.add(int(start))
                            if end.isdigit():
                                years.add(int(end))
                        except ValueError:
                            pass
                    if years:
                        max_year = max(years)
                        min_year = min(years)
                        info["years_of_experience"] = max(1.0, float(max_year - min_year))

        # Extract education
        edu_section = ""
        for header in ["education", "academic background", "qualifications"]:
            idx = text_lower.find(header)
            if idx != -1:
                end = text_lower.find("\n\n", idx + len(header))
                if end == -1:
                    end = min(idx + 500, len(text_lower))
                edu_section = text_lower[idx + len(header):end].strip()
                break
        if edu_section:
            info["education"] = clean_text(edu_section.title())

        # Extract certifications
        cert_section = ""
        for header in ["certifications", "certificates", "licenses"]:
            idx = text_lower.find(header)
            if idx != -1:
                end = text_lower.find("\n\n", idx + len(header))
                if end == -1:
                    end = min(idx + 500, len(text_lower))
                cert_section = text_lower[idx + len(header):end].strip()
                break
        if cert_section:
            info["certifications"] = clean_text(cert_section.title())

        # Extract work experience
        work_section = ""
        for header in ["experience", "work experience", "professional experience"]:
            idx = text_lower.find(header)
            if idx != -1:
                end = text_lower.find("\n\n", idx + len(header))
                if end == -1:
                    end = min(idx + 2000, len(text_lower))
                work_section = text_lower[idx + len(header):end].strip()
                break
        if work_section:
            info["work_experience"] = clean_text(work_section.title())

        return info
