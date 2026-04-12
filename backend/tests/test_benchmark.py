from evaluation.benchmark import BenchmarkRunner
from services.contracts import PipelineOutput


def test_benchmark_runner_returns_three_channels() -> None:
    stub = lambda _: PipelineOutput(answer="ok", score=0.9, latency=1.0)
    runner = BenchmarkRunner(stub, stub, stub)
    result = runner.run("test question")

    assert set(result.keys()) == {"llm", "rag", "graph"}
    assert result["llm"]["answer"] == "ok"
    assert result["rag"]["score"] == 0.9
