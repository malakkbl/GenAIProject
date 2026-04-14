# Backend Artifacts

This directory is the expected home for runtime artifacts used by the web application.

The code in `backend/pipelines/` looks for these logical files:

## RAG artifacts

- `backend/data/rag/chunks.json`
- `backend/data/rag/chunk_embeddings.npy`

Expected chunk format:

```json
[
  {
    "chunk_id": "0_0",
    "article_id": 0,
    "headline": "...",
    "text": "..."
  }
]
```

## GraphRAG artifacts

- `backend/data/graph/knowledge_graph.graphml`
- `backend/data/graph/entity_registry.json`
- `backend/data/graph/community_store.json`
- `backend/data/graph/community_embeddings.npy`

Expected `community_store.json` format:

```json
[
  {
    "community_id": 0,
    "n_entities": 12,
    "entities": ["..."] ,
    "summary": "..."
  }
]
```

If these files are missing, the backend returns a clear error response telling you which logical artifact should be placed here.
