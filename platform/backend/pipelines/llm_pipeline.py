"""Pure LLM pipeline backed by the actual Ollama model."""

from __future__ import annotations

import time

from pipelines.common import ANSWER_MODEL, judge_score, ollama_generate


ANSWER_PROMPT = """You are a precise financial analyst.
Answer the question clearly and concisely using only your knowledge.
If the answer is uncertain, say that you do not know.

Question: {question}

Answer:"""


def run_llm(question: str) -> dict:
    t0 = time.perf_counter()

    answer = ollama_generate(ANSWER_MODEL, ANSWER_PROMPT.format(question=question), timeout=90)
    score = judge_score(question, answer, context=None)

    latency = (time.perf_counter() - t0) * 1000
    return {
        "answer":  answer,
        "score":   round(score, 3),
        "latency": round(latency, 2),
        "metadata": {
            "model": ANSWER_MODEL,
            "mode": "pure_llm",
        },
    }
