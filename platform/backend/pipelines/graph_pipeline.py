"""GraphRAG pipeline backed by graph artifacts exported from the notebook."""

from __future__ import annotations

import json
import re
import time
from functools import lru_cache

import networkx as nx
import numpy as np

from pipelines.common import (
    ANSWER_MODEL,
    GRAPH_DIR,
    JUDGE_MODEL,
    artifact_path,
    judge_score,
    json_safe_load,
    load_embedder,
    missing_artifact_message,
    ollama_generate,
)


GRAPH_PATH = GRAPH_DIR / "knowledge_graph.graphml"
ENTITY_REGISTRY_PATH = GRAPH_DIR / "entity_registry.json"
COMMUNITY_STORE_PATH = GRAPH_DIR / "community_store.json"
COMMUNITY_EMBEDDINGS_PATH = GRAPH_DIR / "community_embeddings.npy"

ANSWER_PROMPT = """You are a financial analyst using a graph-derived context from Bloomberg news.
Answer only from the provided graph context.
If the context does not support the answer, say so explicitly.

Graph context:
{context}

Question: {question}

Answer:"""

QUERY_CLASS_PROMPT = """Classify the question into exactly one routing type:
- local: asks about a specific company, person, or fact
- global: asks about a broad trend, theme, or sector-level pattern
- mixed: needs both a local fact and broader thematic context

Question: {question}

Output only one word: local, global, or mixed."""


@lru_cache(maxsize=1)
def _load_graph_artifacts() -> tuple[nx.MultiDiGraph, dict[str, dict], list[dict], np.ndarray] | None:
    if not all(path.exists() for path in [GRAPH_PATH, ENTITY_REGISTRY_PATH, COMMUNITY_STORE_PATH, COMMUNITY_EMBEDDINGS_PATH]):
        return None

    graph = nx.read_graphml(GRAPH_PATH)
    if not isinstance(graph, nx.MultiDiGraph):
        graph = nx.MultiDiGraph(graph)

    registry = json_safe_load(ENTITY_REGISTRY_PATH, default={}) or {}
    community_store = json_safe_load(COMMUNITY_STORE_PATH, default=[]) or []
    community_embeddings = np.load(COMMUNITY_EMBEDDINGS_PATH, allow_pickle=False)
    return graph, registry, community_store, community_embeddings


def _missing_graph_response() -> dict:
    message = missing_artifact_message(
        "GraphRAG",
        [GRAPH_PATH, ENTITY_REGISTRY_PATH, COMMUNITY_STORE_PATH, COMMUNITY_EMBEDDINGS_PATH],
    )
    return {
        "answer": message,
        "score": 0.0,
        "latency": 0.0,
        "metadata": {
            "missing_artifacts": [
                str(GRAPH_PATH),
                str(ENTITY_REGISTRY_PATH),
                str(COMMUNITY_STORE_PATH),
                str(COMMUNITY_EMBEDDINGS_PATH),
            ],
            "expected_location": str(GRAPH_DIR),
        },
    }


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _extract_question_entities(question: str, registry: dict[str, dict]) -> list[str]:
    q_lower = question.lower()
    matches: list[str] = []

    ticker_candidates = re.findall(r"\(([A-Z]{1,5}(?::[A-Z]{2})?)\)|\$([A-Z]{1,5})\b", question)
    ticker_terms = {item for pair in ticker_candidates for item in pair if item}

    for canonical_id, attrs in registry.items():
        name = _clean_text(str(attrs.get("name", "")))
        if not name:
            continue
        name_lower = name.lower()
        if name_lower in q_lower or any(term.lower() == name_lower for term in ticker_terms):
            matches.append(canonical_id)

    if matches:
        return list(dict.fromkeys(matches))

    capitalized_phrases = re.findall(r"\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b", question)
    for phrase in capitalized_phrases:
        phrase_lower = phrase.lower()
        for canonical_id, attrs in registry.items():
            name = _clean_text(str(attrs.get("name", ""))).lower()
            if phrase_lower in name or name in phrase_lower:
                matches.append(canonical_id)

    return list(dict.fromkeys(matches))


def _serialize_local_context(graph: nx.MultiDiGraph, registry: dict[str, dict], seeds: list[str], depth: int = 2) -> str:
    if not seeds:
        return ""

    frontier = set(seeds)
    visited = set(seeds)
    for _ in range(depth):
        next_frontier = set()
        for node in frontier:
            if graph.has_node(node):
                next_frontier.update(graph.predecessors(node))
                next_frontier.update(graph.successors(node))
        next_frontier -= visited
        visited |= next_frontier
        frontier = next_frontier

    lines: list[str] = []
    for source, target, attrs in graph.edges(data=True):
        if source not in visited or target not in visited:
            continue
        source_name = registry.get(source, {}).get("name", source)
        target_name = registry.get(target, {}).get("name", target)
        relation_type = attrs.get("relation_type", "REL")
        line = f"({source_name}) -[{relation_type}]-> ({target_name})"
        if attrs.get("time_interval"):
            line += f" [{attrs.get('time_interval')}]"
        if attrs.get("confidence"):
            try:
                line += f" conf={float(attrs.get('confidence')):.2f}"
            except Exception:
                pass
        provenance = attrs.get("provenance")
        if provenance:
            try:
                sentence = json.loads(provenance).get("sentence", "")
                if sentence:
                    line += f' | "{sentence[:120]}"'
            except Exception:
                pass
        lines.append(line)

    return "\n".join(lines[:40])


def _serialize_global_context(community_store: list[dict], community_embeddings: np.ndarray, question: str, top_k: int = 3) -> str:
    if community_embeddings.size == 0 or not community_store:
        return ""

    query_vector = load_embedder().encode([question], normalize_embeddings=True)[0].astype(np.float32)
    similarities = community_embeddings @ query_vector
    top_indices = np.argsort(-similarities)[:top_k]

    parts: list[str] = []
    for index in top_indices:
        if index >= len(community_store):
            continue
        community = community_store[int(index)]
        parts.append(
            f"[Community {community.get('community_id', index)} | {community.get('n_entities', 0)} entities]\n"
            f"{community.get('summary', '')}"
        )
    return "\n\n".join(parts)


def _classify_query(question: str) -> str:
    raw = ollama_generate(JUDGE_MODEL, QUERY_CLASS_PROMPT.format(question=question), timeout=60).lower()
    for label in ("local", "global", "mixed"):
        if label in raw:
            return label
    return "mixed"


def run_graph(question: str) -> dict:
    t0 = time.perf_counter()

    loaded = _load_graph_artifacts()
    if loaded is None:
        return _missing_graph_response()

    graph, registry, community_store, community_embeddings = loaded
    query_type = _classify_query(question)
    entity_seeds = _extract_question_entities(question, registry)

    local_context = _serialize_local_context(graph, registry, entity_seeds, depth=2) if query_type in {"local", "mixed"} else ""
    global_context = _serialize_global_context(community_store, community_embeddings, question, top_k=3) if query_type in {"global", "mixed"} else ""

    context_parts = []
    if local_context:
        context_parts.append(f"=== Local Graph Context ===\n{local_context}")
    if global_context:
        context_parts.append(f"=== Community Context ===\n{global_context}")

    context = "\n\n".join(context_parts) if context_parts else "No relevant graph context was found."
    answer = ollama_generate(ANSWER_MODEL, ANSWER_PROMPT.format(context=context, question=question), timeout=120)
    score = judge_score(question, answer, context=context)

    retrieved_article_ids = sorted({
        int(attrs.get("article_id"))
        for _, attrs in registry.items()
        if attrs.get("article_id") not in {None, ""}
        and str(attrs.get("article_id")).isdigit()
    })

    graph_preview = context[:1200]

    latency = (time.perf_counter() - t0) * 1000
    return {
        "answer":   answer,
        "score":    round(score, 3),
        "latency":  round(latency, 2),
        "metadata": {
            "model": ANSWER_MODEL,
            "judge_model": JUDGE_MODEL,
            "query_type": query_type,
            "context_preview": graph_preview,
            "retrieved_article_ids": retrieved_article_ids,
            "artifact_paths": [
                str(GRAPH_PATH),
                str(ENTITY_REGISTRY_PATH),
                str(COMMUNITY_STORE_PATH),
                str(COMMUNITY_EMBEDDINGS_PATH),
            ],
        },
    }
