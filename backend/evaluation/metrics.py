from __future__ import annotations

import re
from typing import Iterable


def heuristic_quality_score(answer: str, context_fragments: Iterable[str] | None = None) -> float:
    if not answer:
        return 0.0

    score = 0.45
    words = answer.split()
    if len(words) >= 20:
        score += 0.15
    if len(words) >= 45:
        score += 0.1

    answer_lc = answer.lower()
    finance_markers = ["revenue", "earnings", "acquisition", "market", "guidance", "profit"]
    if any(marker in answer_lc for marker in finance_markers):
        score += 0.1

    if "insufficient context" in answer_lc:
        score -= 0.2

    if context_fragments:
        joined = " ".join(context_fragments).lower()
        overlap = len(set(re.findall(r"[a-z]{4,}", answer_lc)) & set(re.findall(r"[a-z]{4,}", joined)))
        if overlap > 8:
            score += 0.1

    return max(0.0, min(1.0, round(score, 3)))
