"""Vanilla RAG pipeline backed by real chunk embeddings and Ollama."""

from __future__ import annotations

import time
from functools import lru_cache

import numpy as np

from pipelines.common import ANSWER_MODEL, RAG_DIR, judge_score, json_safe_load, load_embedder, missing_artifact_message, ollama_generate


CHUNK_PATH = RAG_DIR / "chunks.json"
EMBEDDING_PATH = RAG_DIR / "chunk_embeddings.npy"

ANSWER_PROMPT = """You are a financial analyst.
Answer the question using only the retrieved Bloomberg context.
If the context does not support an answer, say so explicitly.

Retrieved context:
{context}

Question: {question}

Answer:"""


@lru_cache(maxsize=1)
def _load_rag_artifacts() -> tuple[list[dict], np.ndarray] | None:
    chunks = json_safe_load(CHUNK_PATH)
    embeddings = np.load(EMBEDDING_PATH, allow_pickle=False) if EMBEDDING_PATH.exists() else None
    if not chunks or embeddings is None:
        return None
    return chunks, embeddings


def _missing_rag_response() -> dict:
    message = missing_artifact_message("RAG", [CHUNK_PATH, EMBEDDING_PATH])
    return {
        "answer": message,
        "score": 0.0,
        "latency": 0.0,
        "metadata": {
            "missing_artifacts": [str(CHUNK_PATH), str(EMBEDDING_PATH)],
            "expected_location": str(RAG_DIR),
        },
    }


def run_rag(question: str) -> dict:
    t0 = time.perf_counter()

    loaded = _load_rag_artifacts()
    if loaded is None:
        return _missing_rag_response()

    chunks, embeddings = loaded
    query_vector = load_embedder().encode([question], normalize_embeddings=True)[0].astype(np.float32)
    similarities = embeddings @ query_vector
    top_indices = np.argsort(-similarities)[:5]

    selected_chunks = [chunks[int(index)] for index in top_indices]
    context = "\n\n".join(
        f"[Article {chunk.get('article_id', 'unknown')} | Chunk {chunk.get('chunk_id', index)}]\n{chunk.get('text', '')}"
        for index, chunk in zip(top_indices, selected_chunks)
    )

    answer = ollama_generate(ANSWER_MODEL, ANSWER_PROMPT.format(context=context, question=question), timeout=120)
    score = judge_score(question, answer, context=context)

    retrieved_article_ids = sorted({chunk.get("article_id") for chunk in selected_chunks if chunk.get("article_id") is not None})
    retrieved_chunk_ids = [chunk.get("chunk_id") for chunk in selected_chunks if chunk.get("chunk_id") is not None]

    latency = (time.perf_counter() - t0) * 1000
    return {
        "answer":   answer,
        "score":    round(score, 3),
        "latency":  round(latency, 2),
        "metadata": {
            "model": ANSWER_MODEL,
            "retrieved_article_ids": retrieved_article_ids,
            "retrieved_chunk_ids": retrieved_chunk_ids,
            "artifact_paths": [str(CHUNK_PATH), str(EMBEDDING_PATH)],
        },
    }
