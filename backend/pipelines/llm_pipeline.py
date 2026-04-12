from __future__ import annotations

import time

from evaluation.metrics import heuristic_quality_score
from llm.client import LLMClient
from llm.prompts import llm_only_system_prompt
from services.contracts import PipelineOutput


class LLMPipeline:
    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    def run(self, question: str) -> PipelineOutput:
        started = time.perf_counter()
        answer = self.llm_client.generate(llm_only_system_prompt(), question)
        latency = (time.perf_counter() - started) * 1000
        score = heuristic_quality_score(answer)
        return PipelineOutput(answer=answer, score=score, latency=round(latency, 2))
