from __future__ import annotations

from threading import Lock

from config.settings import Settings
from data.loader import BloombergDataLoader
from evaluation.benchmark import BenchmarkRunner
from graph.builder import GraphBuilder
from llm.client import LLMClient
from pipelines.graph_pipeline import GraphPipeline
from pipelines.llm_pipeline import LLMPipeline
from pipelines.rag_pipeline import RAGPipeline
from retrieval.embedder import build_embedder
from retrieval.retriever import VanillaRetriever


class PipelineService:
    """Initializes reusable pipeline instances and exposes one benchmark call."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._lock = Lock()
        self._initialized = False
        self.runner: BenchmarkRunner | None = None

    def initialize(self) -> None:
        with self._lock:
            if self._initialized:
                return

            loader = BloombergDataLoader(self.settings)
            articles = loader.load_subset()

            llm_client = LLMClient(self.settings)

            embedder = build_embedder(self.settings)
            retriever = VanillaRetriever(self.settings, embedder)
            retriever.build_index(articles)

            graph_builder = GraphBuilder()
            graph_builder.build(articles)

            llm_pipeline = LLMPipeline(llm_client)
            rag_pipeline = RAGPipeline(self.settings, llm_client, retriever)
            graph_pipeline = GraphPipeline(llm_client, graph_builder)

            self.runner = BenchmarkRunner(
                llm_call=llm_pipeline.run,
                rag_call=rag_pipeline.run,
                graph_call=graph_pipeline.run,
            )
            self._initialized = True

    def benchmark_query(self, question: str) -> dict:
        if not self._initialized:
            self.initialize()
        if self.runner is None:
            raise RuntimeError("Benchmark runner was not initialized")
        return self.runner.run(question)
