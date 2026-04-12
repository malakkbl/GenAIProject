"""
GraphRAG pipeline.

Replace the body of run_graph() with your actual pipeline logic.
The function must return a dict with these keys:
  - answer   (str)   the generated answer
  - score    (float) quality score between 0 and 1
  - latency  (float) time in milliseconds
  - metadata (dict)  optional — the UI will show context_preview if present
                     e.g. {"context_preview": "(Marriott) --[HOLDS_POSITION]--> (Arne Sorenson)"}
"""

import time


def run_graph(question: str) -> dict:
    t0 = time.perf_counter()

    # ── Replace everything below this line with your real GraphRAG logic ─────
    answer = (
        f"[GraphRAG stub] A subgraph was retrieved from the knowledge graph "
        f"for '{question}'. Entity relations were used as context for the LLM. "
        f"Replace this stub with your graph retrieval + LLM call."
    )
    score = 0.75
    metadata = {
        "context_preview": "(Entity A) --[RELATION]--> (Entity B)\n"
                           "(Entity B) --[RELATION]--> (Entity C)",
    }
    # ────────────────────────────────────────────────────────────────────────

    latency = (time.perf_counter() - t0) * 1000
    return {
        "answer":   answer,
        "score":    round(score, 3),
        "latency":  round(latency, 2),
        "metadata": metadata,
    }
