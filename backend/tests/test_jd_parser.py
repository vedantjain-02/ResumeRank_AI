import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.mark.asyncio
async def test_jd_parser_fallback_when_no_api_key():
    from app.services.jd_parser import JDParser

    parser = JDParser()
    parser.api_key = ""  # force fallback

    jd_text = """
    Python Backend Developer
    We are looking for a Python developer with 5 years of experience.
    Required skills: Python, Django, PostgreSQL, Docker.
    Bachelor's degree in Computer Science required.
    """
    parsed = await parser.parse_jd(jd_text)

    assert isinstance(parsed, dict)
    assert "required_skills" in parsed
    assert isinstance(parsed["required_skills"], list)


@pytest.mark.asyncio
async def test_jd_parser_handles_grok_error(mocker):
    from app.services.jd_parser import JDParser
    import httpx

    parser = JDParser()
    parser.api_key = "test-key"

    jd_text = "Software Engineer with 3 years experience in Python."

    mocker.patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("timeout"))
    parsed = await parser.parse_jd(jd_text)

    assert isinstance(parsed, dict)
    assert "required_skills" in parsed