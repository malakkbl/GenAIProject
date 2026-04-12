from __future__ import annotations

from flask import Blueprint, jsonify, request

from services.pipeline_service import PipelineService


def create_query_blueprint(pipeline_service: PipelineService) -> Blueprint:
    bp = Blueprint("query", __name__)

    @bp.post("/query")
    def query() -> tuple:
        payload = request.get_json(silent=True) or {}
        question = str(payload.get("question", "")).strip()
        if not question:
            return jsonify({"error": "question is required"}), 400

        result = pipeline_service.benchmark_query(question)
        return jsonify(result), 200

    @bp.get("/health")
    def health() -> tuple:
        return jsonify({"status": "ok"}), 200

    return bp
