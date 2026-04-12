from flask import Blueprint, request, jsonify
from pipelines.llm_pipeline import run_llm
from pipelines.rag_pipeline import run_rag
from pipelines.graph_pipeline import run_graph
import concurrent.futures
import time

query_bp = Blueprint("query", __name__)


@query_bp.get("/health")
def health():
    return jsonify({"status": "ok"})


@query_bp.post("/query")
def query():
    data = request.get_json(silent=True) or {}
    question = str(data.get("question", "")).strip()

    if not question:
        return jsonify({"error": "question is required"}), 400

    # Run all three pipelines in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        f_llm   = ex.submit(run_llm,   question)
        f_rag   = ex.submit(run_rag,   question)
        f_graph = ex.submit(run_graph, question)

        llm_result   = f_llm.result()
        rag_result   = f_rag.result()
        graph_result = f_graph.result()

    return jsonify({
        "llm":   llm_result,
        "rag":   rag_result,
        "graph": graph_result,
    })
