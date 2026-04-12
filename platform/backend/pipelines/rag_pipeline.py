"""
Vanilla RAG pipeline.

Replace the body of run_rag() with your actual pipeline logic.
The function must return a dict with these keys:
  - answer   (str)   the generated answer
  - score    (float) quality score between 0 and 1
  - latency  (float) time in milliseconds
  - metadata (dict)  optional — the UI will show retrieved_article_ids if present
                     e.g. {"retrieved_article_ids": [0, 4, 12]}
"""

import time


def run_rag(question: str) -> dict:
    t0 = time.perf_counter()

    # ── Replace everything below this line with your real RAG logic ──────────
    answer = (
        f"[Vanilla RAG stub] Top-k chunks were retrieved from the Bloomberg corpus "
        f"and passed as context for '{question}'. "
        f"Replace this stub with your FAISS retrieval + LLM call."
    )
    score = 0.60
    metadata = {
        "retrieved_article_ids": [0, 3, 7],   # replace with real retrieved IDs
    }
    # ────────────────────────────────────────────────────────────────────────

    latency = (time.perf_counter() - t0) * 1000
    return {
        "answer":   answer,
        "score":    round(score, 3),
        "latency":  round(latency, 2),
        "metadata": metadata,
    }
