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
        f"[Pure LLM stub] No retrieval was used. "
        f"The model answered '{question}' from parametric memory only. "
        f"Replace this stub with your Mistral / Ollama call."
    )
    score = 0.50
    # ────────────────────────────────────────────────────────────────────────

    latency = (time.perf_counter() - t0) * 1000
    return {
        "answer":  answer,
        "score":   round(score, 3),
        "latency": round(latency, 2),
    }
