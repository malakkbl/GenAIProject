from __future__ import annotations

import json
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

import numpy as np
import requests
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAG_DIR = DATA_DIR / "rag"
GRAPH_DIR = DATA_DIR / "graph"

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
ANSWER_MODEL = os.environ.get("ANSWER_MODEL", "mistral-nemo")
JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "llama3.2:3b")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


def artifact_path(*parts: str) -> Path:
    return DATA_DIR.joinpath(*parts)


def missing_artifact_message(kind: str, paths: list[Path]) -> str:
    expected = ", ".join(str(path.relative_to(BASE_DIR)) for path in paths)
    return (
        f"Missing {kind} artifacts. Place the required files under {expected}. "
        f"See {DATA_DIR.relative_to(BASE_DIR) / 'README.md'} for the expected layout."
    )


def _extract_json_object(raw: str) -> Optional[dict[str, Any]]:
    try:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        return json.loads(match.group()) if match else None
    except Exception:
        return None


def ollama_generate(model: str, prompt: str, timeout: int = 90) -> str:
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": model, "prompt": prompt, "stream": False, "options": {"temperature": 0.0}},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json().get("response", "").strip()


@lru_cache(maxsize=1)
def load_embedder() -> SentenceTransformer:
    return SentenceTransformer(EMBED_MODEL, device="cpu")


def judge_score(question: str, answer: str, context: str | None = None) -> float:
    if context:
        prompt = (
            "Rate answer quality on a 0.0-1.0 scale.\n"
            "Use the provided question and context. Score higher when the answer is grounded, relevant, and specific.\n\n"
            f"Question: {question}\n\n"
            f"Context: {context}\n\n"
            f"Answer: {answer}\n\n"
            'Output ONLY JSON: {"score": <float>, "reason": "<one sentence>"}'
        )
    else:
        prompt = (
            "Rate answer quality on a 0.0-1.0 scale.\n"
            "Score higher when the answer is directly responsive and internally consistent.\n\n"
            f"Question: {question}\n\n"
            f"Answer: {answer}\n\n"
            'Output ONLY JSON: {"score": <float>, "reason": "<one sentence>"}'
        )

    raw = ollama_generate(JUDGE_MODEL, prompt, timeout=60)
    obj = _extract_json_object(raw) or {}
    try:
        score = float(obj.get("score", 0.0))
    except Exception:
        score = 0.0
    return max(0.0, min(1.0, score))


def json_safe_load(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def np_safe_load(path: Path) -> np.ndarray | None:
    if not path.exists():
        return None
    return np.load(path, allow_pickle=False)
