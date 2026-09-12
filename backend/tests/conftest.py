import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def pytest_configure(config):
    os.environ.setdefault("DATABASE_URL", "postgresql://postgres:password@localhost:5432/resume_screening")
    os.environ.setdefault("GROK_API_KEY", "")


@pytest.fixture(autouse=True)
def _patch_generate_embedding(monkeypatch):
    """Keep unit tests hermetic and fast: never load the SentenceTransformer model.

    The fixed vector only needs to be non-empty; candidate resume_embeddings are
    None (or explicit vectors in hybrid tests), so real semantic scoring is not
    exercised here. Live/DB tests intentionally re-enable the real generator.
    """
    from app.services.embedding_service import embedding_service

    monkeypatch.setattr(
        embedding_service,
        "generate_embedding",
        lambda text: [0.1] * 384 if text else None,
    )