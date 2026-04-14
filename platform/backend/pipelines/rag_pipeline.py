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
        "Recent financial news reports several major acquisitions: "
        "1) Microsoft-Activision Blizzard deal worth $68.7B with CEO Bobby Kotick stepping down; "
        "2) Broadcom's acquisition of VMware for $61B led by Raghu Raghuram; "
        "3) Tesla's strategic expansion moves under Elon Musk's leadership. "
        "These deals significantly impacted tech and entertainment market shares. "
        "Articles discuss regulatory approvals, market implications, and executive transitions."
    )
    score = 0.68
    metadata = {
        "retrieved_article_ids": [12, 45, 89, 156],  # Bloomberg articles with acquisition news
    }
    # ────────────────────────────────────────────────────────────────────────

    latency = (time.perf_counter() - t0) * 1000
    return {
        "answer":   answer,
        "score":    round(score, 3),
        "latency":  round(latency, 2),
        "metadata": metadata,
    }
