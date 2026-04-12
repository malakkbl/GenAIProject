# Notebook-to-Production Formalization

## Source Notebooks

- notebooks/ForBenchmark/Baseline1PureLLMQA.ipynb
- notebooks/ForBenchmark/Baseline2VanillaRAGQA.ipynb
- notebooks/KnowledgeGraphPaper2/graph_generation.ipynb

## 1. Pipeline Data Flows

### Pure LLM (Baseline 1)

- Input: user question
- Processing:
  - inject question into analyst-oriented system prompt
  - invoke LLM without external context
- Output:
  - direct answer from model parametric memory

### Vanilla RAG (Baseline 2)

- Input: user question
- Processing:
  - split dataset articles into overlapping chunks
  - embed all chunks
  - retrieve top-k chunks by similarity
  - inject retrieved chunks in prompt
  - call LLM for grounded answer
- Output:
  - answer + retrieval metadata

### Graph Pipeline (graph_generation)

- Input: user question
- Processing:
  - extract relation-bearing graph from corpus
  - maintain canonical entity ids and provenance-rich edges
  - retrieve local graph context based on query entities
  - inject graph context into grounded prompt
  - call LLM
- Output:
  - graph-grounded answer

## 2. Model Usage Patterns

- Chat-like instruction prompting with financial analyst role.
- Deterministic/low-temperature generation for stable benchmarking.
- Context-specific prompts:
  - none for pure LLM
  - top-k raw chunks for vanilla RAG
  - subgraph edge context for graph mode

## 3. Graph Construction Logic

- Entities: organization/person-like mentions with alias-to-canonical mapping.
- Relations: seeded financial patterns (acquired, merged_with, invested_in, partner_of).
- Edge attributes:
  - predicate
  - timestamp (when inferred)
  - provenance snippet/chunk id
  - confidence score
- Storage: NetworkX MultiDiGraph, optional GraphML persistence.

## 4. Prompt Engineering Strategy

- LLM-only prompt: concise answer from financial knowledge.
- RAG prompt: explicit instruction to use retrieved context first.
- Graph prompt: explicit instruction to rely on graph evidence and report insufficiency.

## 5. Evaluation Translation

Notebook offline metrics (ROUGE-L + LLM judge) are preserved as methodology.
Production online API returns a fast confidence/quality heuristic + latency per mode for interactive use.

For strict offline benchmarking with references, extend evaluation/metrics.py with notebook-equivalent batch metrics.
