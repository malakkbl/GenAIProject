from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable
import hashlib

import numpy as np

from config.settings import Settings


class BaseEmbedder(ABC):
    @abstractmethod
    def encode(self, texts: Iterable[str]) -> np.ndarray:
        raise NotImplementedError


class HashEmbedder(BaseEmbedder):
    """Deterministic fallback embedding when sentence-transformers is unavailable."""

    def __init__(self, dim: int = 384) -> None:
        self.dim = dim

    def _vectorize(self, text: str) -> np.ndarray:
        vec = np.zeros(self.dim, dtype=np.float32)
        for token in text.lower().split():
            h = int(hashlib.md5(token.encode()).hexdigest(), 16)
            vec[h % self.dim] += 1.0
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec

    def encode(self, texts: Iterable[str]) -> np.ndarray:
        return np.vstack([self._vectorize(t) for t in texts]).astype(np.float32)


class SentenceTransformerEmbedder(BaseEmbedder):
    def __init__(self, model_name: str) -> None:
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name, device="cpu")

    def encode(self, texts: Iterable[str]) -> np.ndarray:
        vectors = self.model.encode(list(texts), normalize_embeddings=True)
        return np.array(vectors, dtype=np.float32)


def build_embedder(settings: Settings) -> BaseEmbedder:
    try:
        return SentenceTransformerEmbedder(settings.embedding_model)
    except Exception:
        return HashEmbedder()
