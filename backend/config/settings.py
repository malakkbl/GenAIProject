from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("APP_PORT", "5000"))
    debug: bool = os.getenv("APP_DEBUG", "false").lower() == "true"

    dataset_name: str = os.getenv("DATASET_NAME", "XJCEO/bloomberg_financial_news_120k")
    dataset_split: str = os.getenv("DATASET_SPLIT", "train")
    dataset_subset_size: int = int(os.getenv("DATASET_SUBSET_SIZE", "5000"))

    llm_backend: str = os.getenv("LLM_BACKEND", "ollama")
    llm_model: str = os.getenv("LLM_MODEL", "mistral-nemo")
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    llm_max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "350"))

    ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434")

    embedding_model: str = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "512"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "64"))
    top_k: int = int(os.getenv("TOP_K", "5"))

    graph_file: str = os.getenv("GRAPH_FILE", "backend/graph_store.graphml")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
