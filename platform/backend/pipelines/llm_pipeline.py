"""
Pure LLM pipeline.

Replace the body of run_llm() with your actual pipeline logic.
The function must return a dict with these keys:
  - answer   (str)   the generated answer
  - score    (float) quality score between 0 and 1
  - latency  (float) time in milliseconds
  - metadata (dict)  any extra info you want shown in the UI (optional)
"""

import time


def run_llm(question: str) -> dict:
    t0 = time.perf_counter()

    # ── Replace everything below this line with your real LLM call ──────────
    answer = (
        "Based on my training data, several major tech acquisitions were announced: "
        "Microsoft acquired Activision Blizzard for $68.7 billion, "
        "and Elon Musk was involved in major Tesla strategic moves. "
        "However, without current context, I cannot provide specific dates or recent developments. "
        "This answer lacks recent financial news context."
    )
    score = 0.52
    # ────────────────────────────────────────────────────────────────────────

    latency = (time.perf_counter() - t0) * 1000
    return {
        "answer":  answer,
        "score":   round(score, 3),
        "latency": round(latency, 2),
    }
