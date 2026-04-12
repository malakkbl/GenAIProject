from __future__ import annotations

from dataclasses import dataclass
from typing import List

from config.settings import Settings
from retrieval.embedder import BaseEmbedder
from retrieval.vector_store import InMemoryVectorStore


@dataclass
class ChunkingConfig:
    chunk_size: int
    chunk_overlap: int


class TextChunker:
    def __init__(self, config: ChunkingConfig) -> None:
        self.config = config
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter

            self._splitter = RecursiveCharacterTextSplitter(
                chunk_size=config.chunk_size,
                chunk_overlap=config.chunk_overlap,
                separators=["\n\n", "\n", ". ", " ", ""],
            )
        except Exception:
            self._splitter = None

    def split(self, text: str) -> List[str]:
        if self._splitter is not None:
            return [c for c in self._splitter.split_text(text) if len(c.strip()) > 20]

        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        out: List[str] = []
        i = 0
        while i < len(text):
            part = text[i : i + chunk_size].strip()
            if len(part) > 20:
                out.append(part)
            i += max(1, chunk_size - overlap)
        return out


class VanillaRetriever:
    def __init__(self, settings: Settings, embedder: BaseEmbedder) -> None:
        self.settings = settings
        self.embedder = embedder
        self.vector_store = InMemoryVectorStore()
        self.chunker = TextChunker(
            ChunkingConfig(
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap,
            )
        )
        self._ready = False

    def build_index(self, articles: List[dict]) -> None:
        chunks: List[dict] = []
        for article in articles:
            split_chunks = self.chunker.split(article["text"])
            for text in split_chunks:
                chunks.append(
                    {
                        "article_id": article["article_id"],
                        "headline": article.get("headline", ""),
                        "text": text,
                    }
                )
        vectors = self.embedder.encode([c["text"] for c in chunks])
        self.vector_store.add(vectors, chunks)
        self._ready = True

    def retrieve(self, question: str, top_k: int | None = None) -> List[dict]:
        if not self._ready:
            return []
        k = top_k or self.settings.top_k
        qv = self.embedder.encode([question])[0]
        return self.vector_store.search(qv, top_k=k)
