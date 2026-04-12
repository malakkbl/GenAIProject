from __future__ import annotations

import json
from typing import Any
import requests

from config.settings import Settings


class LLMClient:
    """Simple model client supporting local Ollama backend."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _ollama_generate(self, system_prompt: str, user_prompt: str) -> str:
        prompt = f"System: {system_prompt}\n\nUser: {user_prompt}\n\nAssistant:"
        payload = {
            "model": self.settings.llm_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.settings.llm_temperature,
            },
        }
        response = requests.post(
            f"{self.settings.ollama_url}/api/generate", json=payload, timeout=120
        )
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        return str(data.get("response", "")).strip()

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        try:
            if self.settings.llm_backend == "ollama":
                return self._ollama_generate(system_prompt, user_prompt)
            return "LLM backend not configured."
        except Exception as exc:
            return f"[LLM error] {exc}"

    def judge_answer_confidence(self, answer: str, context: str = "") -> float:
        """Fast confidence heuristic for online comparison endpoint."""
        if not answer:
            return 0.0
        score = 0.5
        token_count = len(answer.split())
        if token_count > 20:
            score += 0.1
        if token_count > 50:
            score += 0.1
        if context and any(marker in answer.lower() for marker in ["according", "reported", "context"]):
            score += 0.1
        if "insufficient context" in answer.lower():
            score -= 0.2
        return max(0.0, min(1.0, round(score, 3)))

    def parse_json(self, raw: str) -> dict:
        try:
            start = raw.find("{")
            end = raw.rfind("}")
            if start >= 0 and end > start:
                return json.loads(raw[start : end + 1])
        except Exception:
            return {}
        return {}
