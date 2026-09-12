import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(autouse=True)
def _reset_presentation_lines():
    from app.services.jd_parser import _PRESENTATION_LINES
    _PRESENTATION_LINES.clear()
    _PRESENTATION_LINES.append(None)
    yield


def parse(jd_text, max_mandatory=10):
    from app.services.jd_parser import parse_skill_structure
    return parse_skill_structure(jd_text, max_mandatory=max_mandatory)


# ----------------------------------------------------------------------
# 1. Mandatory skills come ONLY from explicitly required sections
# ----------------------------------------------------------------------

def test_mandatory_only_from_required_section():
    jd = """
    Senior AI/ML Engineer
    About the Role:
    We are building an ML platform and need a strong engineer.
    Key Responsibilities:
    - Build training pipelines, tune models, optimise inference.
    Required Technical Skills:
    - Python
    - PyTorch
    - TensorFlow
    - SQL
    - Snowflake
    Preferred Skills:
    - FastAPI
    - Flask
    - Kubernetes
    - Docker
    - Terraform
    Nice to Have:
    - Airflow
    """
    parsed = parse(jd)
    mandatory = parsed["mandatory_skills"]
    assert "python" in mandatory
    assert "pytorch" in mandatory
    assert "snowflake" in mandatory
    # preferred / responsibilities skills must never be mandatory
    assert "fastapi" not in mandatory
    assert "flask" not in mandatory
    assert "kubernetes" not in mandatory
    assert "airflow" not in mandatory


def test_skills_in_responsibilities_are_not_mandatory():
    jd = """
    Backend Engineer
    Key Responsibilities:
    - Write services with FastAPI and Flask.
    - Manage Postgres and Redis.
    Requirements:
    - Python
    - SQL
    """
    parsed = parse(jd)
    mandatory = parsed["mandatory_skills"]
    assert set(mandatory) <= {"python", "sql"}
    assert "fastapi" not in mandatory
    assert "flask" not in mandatory


def test_section_inline_colon_headers_parsed():
    jd = """
    Data Engineer
    Required skills: Python, Airflow, Spark, Docker.
    Preferred skills: Kubernetes, Snowflake.
    """
    parsed = parse(jd)
    mandatory = parsed["mandatory_skills"]
    assert "python" in mandatory
    assert "spark" in mandatory
    assert "kubernetes" not in mandatory


# ----------------------------------------------------------------------
# 2. Mandatory cap
# ----------------------------------------------------------------------

def test_mandatory_capped_at_10():
    many = ", ".join(
        ("python", "java", "golang", "rust", "react", "angular", "node.js",
         "django", "flask", "fastapi", "postgresql", "mongodb", "redis",
         "aws", "docker", "kubernetes", "terraform", "airflow", "spark",
         "pytorch", "pandas", "mlflow", "graphql", "grpc", "howdoesseldom")
    )
    jd = f"""
    Platform Engineer
    Required Technical Skills:
    {many}
    """
    parsed = parse(jd, max_mandatory=10)
    assert len(parsed["mandatory_skills"]) <= 10
    # whatever the cap dropped stays visible as inferred (never lost)
    assert len(parsed["inferred_skills"]) >= 14


def test_parse_skill_structure_respects_custom_cap():
    jd = """
    ML Engineer
    Required Skills:
    - Python, PyTorch, TensorFlow, SQL, Snowflake, BigQuery, MLflow, NLP, C++.
    """
    parsed = parse(jd, max_mandatory=5)
    assert len(parsed["mandatory_skills"]) == 5


# ----------------------------------------------------------------------
# 3. Skill lists are normalized
# ----------------------------------------------------------------------

def test_skill_lists_are_deduped_and_lowercased():
    jd = """
    Backend Developer
    Required Skills:
    - Python, Python, SQL, SQL
    Preferred Skills:
    - Docker, docker, Kubernetes
    """
    parsed = parse(jd)
    assert parsed["mandatory_skills"].count("python") == 1
    assert parsed["preferred_skills"].count("docker") == 1


# ----------------------------------------------------------------------
# 4. Fallback parser end-to-end
# ----------------------------------------------------------------------

@pytest.mark.asyncio
async def test_fallback_parser_section_aware():
    from app.services.jd_parser import JDParser
    parser = JDParser()
    parser.api_key = ""  # force fallback
    jd = """
    Senior AI/ML Engineer
    Responsibilities:
    - Deploy models with FastAPI and Flask.
    Required Technical Skills:
    - Python, PyTorch, TensorFlow, SQL, Snowflake, BigQuery.
    Preferred Skills:
    - Kubernetes, Docker, Terraform.
    """
    parsed = await parser.parse_jd(jd)
    assert "fastapi" not in parsed["mandatory_skills"]
    assert "flask" not in parsed["mandatory_skills"]
    assert "python" in parsed["mandatory_skills"]
    assert "fastapi" not in parsed["required_skills"]


# ----------------------------------------------------------------------
# 5. Education extraction
# ----------------------------------------------------------------------

def test_education_extracted_from_required_section():
    from app.services.jd_parser import _extract_education
    text = "Bachelor's degree in Computer Science, or equivalent experience. Python required."
    edu = _extract_education(text)
    assert edu != "Not specified"
    assert "bachelor" in edu.lower()


def test_education_missing_when_no_keyword():
    from app.services.jd_parser import _extract_education
    assert _extract_education("No degree mentioned anywhere here.") == "Not specified"