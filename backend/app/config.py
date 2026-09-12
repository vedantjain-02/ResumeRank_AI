from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import Dict


class Settings(BaseSettings):
    DATABASE_URL: str = ""
    GROK_API_KEY: str = ""
    GROK_API_URL: str = "https://api.x.ai/v1/chat/completions"
    GROK_MODEL: str = "grok-4.6"

    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    UPLOAD_DIR: str = "./uploads"

    SCORING_WEIGHTS_SKILLS: float = 0.40
    SCORING_WEIGHTS_EXPERIENCE: float = 0.25
    SCORING_WEIGHTS_SEMANTIC: float = 0.20
    SCORING_WEIGHTS_EDUCATION: float = 0.15
    SCORING_WEIGHTS: Dict[str, float] = {}

    MANDATORY_SKILL_PENALTY: float = 0.3
    PREFERRED_SKILL_BONUS: float = 0.1
    DEFAULT_RANKING_LIMIT: int = 5

    HARD_FILTER_MIN_EXPERIENCE: bool = True
    HARD_FILTER_MAX_EXPERIENCE: bool = True
    HARD_FILTER_SENIORITY: bool = True
    HARD_FILTER_SENIORITY_TOLERANCE: int = 1
    HARD_FILTER_MANDATORY_SKILLS: bool = True
    HARD_FILTER_EDUCATION: bool = True
    HARD_FILTER_RELAX_ON_EMPTY: bool = True
    MAX_MANDATORY_SKILLS: int = 10

    HARD_FILTER_MAX_POOL_SIZE: int = 50
    HARD_FILTER_MIN_POOL_SIZE: int = 40

    BM25_RETRIEVAL_LIMIT: int = 50
    VECTOR_RETRIEVAL_LIMIT: int = 50

    FUSION_BM25_WEIGHT: float = 0.4
    FUSION_VECTOR_WEIGHT: float = 0.6
    FUSION_LIMIT: int = 50

    FINAL_SCORE_HYBRID_WEIGHT: float = 0.25
    FINAL_SCORE_DETAILED_WEIGHT: float = 0.75
    FINAL_SCORE_ENABLE_HYBRID: bool = True
    FINAL_SCORE_ENABLE_MANDATORY_PRIORITY: bool = True
    FINAL_SCORE_MANDATORY_PENALTY: float = 5.0

    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: set = {".pdf", ".docx"}

    @model_validator(mode="after")
    def build_weights(self) -> "Settings":
        self.SCORING_WEIGHTS = {
            "skills": self.SCORING_WEIGHTS_SKILLS,
            "experience": self.SCORING_WEIGHTS_EXPERIENCE,
            "semantic": self.SCORING_WEIGHTS_SEMANTIC,
            "education": self.SCORING_WEIGHTS_EDUCATION,
        }
        return self

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()