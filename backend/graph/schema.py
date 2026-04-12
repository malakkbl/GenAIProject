from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Entity:
    text: str
    entity_type: str


@dataclass
class Provenance:
    source_chunk_id: str
    raw_sentence: str


@dataclass
class Relation:
    subject: str
    predicate: str
    obj: str
    time_start: str | None
    provenance: Provenance
    confidence: float
