from __future__ import annotations

import time

from config.settings import Settings
from evaluation.metrics import heuristic_quality_score
from llm.client import LLMClient
from llm.prompts import build_rag_user_prompt, rag_system_prompt
from retrieval.retriever import VanillaRetriever
from services.contracts import PipelineOutput


class RAGPipeline:
    def __init__(self, settings: Settings, llm_client: LLMClient, retriever: VanillaRetriever) -> None:
        self.settings = settings
        self.llm_client = llm_client
        self.retriever = retriever

    def run(self, question: str) -> PipelineOutput:
        started = time.perf_counter()
        retrieved = self.retriever.retrieve(question, top_k=self.settings.top_k)
        user_prompt = build_rag_user_prompt(question, retrieved)
        answer = self.llm_client.generate(rag_system_prompt(), user_prompt)
        latency = (time.perf_counter() - started) * 1000
        score = heuristic_quality_score(answer, [chunk["text"] for chunk in retrieved])

        metadata = {
            "top_k": self.settings.top_k,
            "retrieved_article_ids": [c["article_id"] for c in retrieved],
        }
        return PipelineOutput(
            answer=answer,
            score=score,
            latency=round(latency, 2),
            metadata=metadata,
        )
