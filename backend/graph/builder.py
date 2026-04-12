from __future__ import annotations

import hashlib
import re
from typing import Dict, List

import networkx as nx

from graph.schema import Provenance, Relation


ALIAS_TABLE: Dict[str, str] = {
    "Goldman Sachs": "LEI:549300IUPX6KIT9GK103",
    "Goldman": "LEI:549300IUPX6KIT9GK103",
    "GS": "LEI:549300IUPX6KIT9GK103",
    "Apple": "GID:AAPL",
    "Microsoft": "GID:MSFT",
    "JPMorgan": "LEI:7H6GLXDRUGQFU57RNE97",
    "JP Morgan": "LEI:7H6GLXDRUGQFU57RNE97",
    "OpenAI": "GID:OPENAI",
}

ENTITY_PATTERN = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b")
YEAR_PATTERN = re.compile(r"\b(20\d{2}|19\d{2})\b")

REL_PATTERNS = [
    (re.compile(r"(?P<subj>[A-Z][\w ]{1,30})\s+acquired\s+(?P<obj>[A-Z][\w ]{1,30})", re.I), "acquired"),
    (re.compile(r"(?P<subj>[A-Z][\w ]{1,30})\s+merged\s+with\s+(?P<obj>[A-Z][\w ]{1,30})", re.I), "merged_with"),
    (re.compile(r"(?P<subj>[A-Z][\w ]{1,30})\s+invested\s+in\s+(?P<obj>[A-Z][\w ]{1,30})", re.I), "invested_in"),
    (re.compile(r"(?P<subj>[A-Z][\w ]{1,30})\s+partnered\s+with\s+(?P<obj>[A-Z][\w ]{1,30})", re.I), "partner_of"),
]


class GraphBuilder:
    def __init__(self) -> None:
        self.graph = nx.MultiDiGraph()

    def _canonical_id(self, name: str) -> str:
        if name in ALIAS_TABLE:
            return ALIAS_TABLE[name]
        return f"LOCAL:{hashlib.md5(name.lower().encode()).hexdigest()[:10]}"

    def _extract_relations(self, text: str, chunk_id: str) -> List[Relation]:
        relations: List[Relation] = []
        for pattern, rel_type in REL_PATTERNS:
            for match in pattern.finditer(text):
                subj = match.group("subj").strip()
                obj = match.group("obj").strip()
                if subj.lower() == obj.lower():
                    continue
                year_match = YEAR_PATTERN.search(text)
                ts = f"{year_match.group(1)}-01-01" if year_match else None
                relations.append(
                    Relation(
                        subject=subj,
                        predicate=rel_type,
                        obj=obj,
                        time_start=ts,
                        provenance=Provenance(source_chunk_id=chunk_id, raw_sentence=text[:300]),
                        confidence=0.7,
                    )
                )
        return relations

    def ingest_article(self, article: dict) -> List[Relation]:
        text = article["text"]
        chunk_id = hashlib.md5(f"{article['article_id']}:0".encode()).hexdigest()[:12]
        relations = self._extract_relations(text, chunk_id)

        for rel in relations:
            src_id = self._canonical_id(rel.subject)
            dst_id = self._canonical_id(rel.obj)
            self.graph.add_node(src_id, name=rel.subject)
            self.graph.add_node(dst_id, name=rel.obj)
            self.graph.add_edge(
                src_id,
                dst_id,
                rel=rel.predicate,
                time_start=rel.time_start,
                provenance_sentence=rel.provenance.raw_sentence,
                provenance_chunk_id=rel.provenance.source_chunk_id,
                confidence=rel.confidence,
                article_id=article["article_id"],
            )
        return relations

    def build(self, articles: List[dict]) -> nx.MultiDiGraph:
        for article in articles:
            self.ingest_article(article)
        return self.graph

    def query_context(self, question: str, max_edges: int = 8) -> str:
        if self.graph.number_of_edges() == 0:
            return "No graph context available."

        aliases = [alias for alias in ALIAS_TABLE if alias.lower() in question.lower()]
        seed_ids = [self._canonical_id(alias) for alias in aliases if self._canonical_id(alias) in self.graph]

        edges = []
        if seed_ids:
            for node in seed_ids:
                for src, dst, data in self.graph.out_edges(node, data=True):
                    edges.append((src, dst, data))
                for src, dst, data in self.graph.in_edges(node, data=True):
                    edges.append((src, dst, data))
        else:
            edges = list(self.graph.edges(data=True))

        lines = ["[Graph Context]"]
        for src, dst, data in edges[:max_edges]:
            src_name = self.graph.nodes[src].get("name", src)
            dst_name = self.graph.nodes[dst].get("name", dst)
            ts = data.get("time_start") or "unknown"
            lines.append(f"({src_name}) --[{data.get('rel', '?')}]--> ({dst_name}) @ {ts}")
            prov = str(data.get("provenance_sentence", ""))
            if prov:
                lines.append(f"  provenance: {prov[:140]}")
        return "\n".join(lines)
