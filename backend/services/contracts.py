from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class PipelineOutput:
    answer: str
    score: float
    latency: float
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if payload["metadata"] is None:
            payload.pop("metadata")
        return payload
