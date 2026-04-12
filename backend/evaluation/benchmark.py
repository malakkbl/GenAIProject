from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Callable

from services.contracts import PipelineOutput


class BenchmarkRunner:
    """Executes all QA paradigms in parallel for direct online comparison."""

    def __init__(
        self,
        llm_call: Callable[[str], PipelineOutput],
        rag_call: Callable[[str], PipelineOutput],
        graph_call: Callable[[str], PipelineOutput],
    ) -> None:
        self.llm_call = llm_call
        self.rag_call = rag_call
        self.graph_call = graph_call

    def run(self, question: str) -> dict:
        with ThreadPoolExecutor(max_workers=3) as executor:
            llm_future = executor.submit(self.llm_call, question)
            rag_future = executor.submit(self.rag_call, question)
            graph_future = executor.submit(self.graph_call, question)

            llm_out = llm_future.result()
            rag_out = rag_future.result()
            graph_out = graph_future.result()

        return {
            "llm": llm_out.to_dict(),
            "rag": rag_out.to_dict(),
            "graph": graph_out.to_dict(),
        }
