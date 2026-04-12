from __future__ import annotations

import time

from evaluation.metrics import heuristic_quality_score
from graph.builder import GraphBuilder
from llm.client import LLMClient
from llm.prompts import build_graph_user_prompt, graph_system_prompt
from services.contracts import PipelineOutput


class GraphPipeline:
    def __init__(self, llm_client: LLMClient, graph_builder: GraphBuilder) -> None:
        self.llm_client = llm_client
        self.graph_builder = graph_builder

    def run(self, question: str) -> PipelineOutput:
        started = time.perf_counter()
        context = self.graph_builder.query_context(question)
        user_prompt = build_graph_user_prompt(question, context)
        answer = self.llm_client.generate(graph_system_prompt(), user_prompt)
        latency = (time.perf_counter() - started) * 1000
        score = heuristic_quality_score(answer, [context])
        metadata = {"context_preview": context[:200]}
        return PipelineOutput(
            answer=answer,
            score=score,
            latency=round(latency, 2),
            metadata=metadata,
        )
