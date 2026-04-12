from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import networkx as nx

from graph.schema import Relation


class GraphStorage:
    def __init__(self, graph_path: str) -> None:
        self.graph_path = Path(graph_path)

    def save_graphml(self, graph: nx.MultiDiGraph) -> None:
        self.graph_path.parent.mkdir(parents=True, exist_ok=True)
        nx.write_graphml(graph, self.graph_path)

    def load_graphml(self) -> nx.MultiDiGraph | None:
        if not self.graph_path.exists():
            return None
        return nx.read_graphml(self.graph_path)

    def save_edges_jsonl(self, relations: Iterable[Relation], output_path: str) -> None:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as f:
            for rel in relations:
                payload = {
                    "subj": rel.subject,
                    "rel": rel.predicate,
                    "obj": rel.obj,
                    "time": {"start": rel.time_start, "end": None},
                    "provenance": {
                        "source_chunk_id": rel.provenance.source_chunk_id,
                        "raw_sentence": rel.provenance.raw_sentence,
                    },
                    "confidence": rel.confidence,
                }
                f.write(json.dumps(payload) + "\n")
