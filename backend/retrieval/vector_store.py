from __future__ import annotations

from typing import List

import numpy as np


class InMemoryVectorStore:
    def __init__(self) -> None:
        self.vectors: np.ndarray | None = None
        self.metadata: List[dict] = []

    def add(self, vectors: np.ndarray, metadata: List[dict]) -> None:
        if self.vectors is None:
            self.vectors = vectors
        else:
            self.vectors = np.vstack([self.vectors, vectors])
        self.metadata.extend(metadata)

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[dict]:
        if self.vectors is None or not self.metadata:
            return []

        sims = self.vectors @ query_vector.reshape(-1)
        top_indices = np.argsort(-sims)[:top_k]
        results = []
        for idx in top_indices:
            chunk = dict(self.metadata[idx])
            chunk["score"] = float(sims[idx])
            results.append(chunk)
        return results
