from sentence_transformers import SentenceTransformer
import numpy as np
import logging
from typing import List, Optional
from app.config import settings

logger = logging.getLogger(__name__)

_model_instance = None


class EmbeddingService:
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL_NAME
        self._model = None

    @property
    def model(self):
        global _model_instance
        if _model_instance is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            _model_instance = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully.")
        return _model_instance

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        if not text:
            return None
        try:
            embedding = self.model.encode(text, normalize_embeddings=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    def generate_batch_embeddings(self, texts: List[str]) -> List[Optional[List[float]]]:
        valid_texts = [t if t else "" for t in texts]
        try:
            embeddings = self.model.encode(valid_texts, normalize_embeddings=True, show_progress_bar=False)
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            return [None] * len(texts)

    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        if embedding1 is None or embedding2 is None or len(embedding1) == 0 or len(embedding2) == 0:
            return 0.0
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            similarity = float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
            return max(0.0, min(1.0, similarity))
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            return 0.0


embedding_service = EmbeddingService()
