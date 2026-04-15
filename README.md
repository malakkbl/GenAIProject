# Financial QA Comparison Platform

**By students:** Malak Kably & Safae Hajjout
**Supervised by:** Pr.Lamiae Azizi
**Spring Semester 2026**

This project studies how GraphRAG can improve question answering over financial news, and exposes the comparison through a small web application:

1. Pure LLM QA, with no retrieval.
2. Vanilla RAG, using chunk retrieval over the article corpus.
3. GraphRAG, using entity and relation structure extracted from the same corpus.

The goal is to show how relational structure changes answer quality on finance-specific questions, especially when the question depends on multiple facts in the same article or across related articles.

## Project Purpose

The notebooks in this repository formalize an end-to-end GraphRAG benchmark for financial news. The main idea is to turn Bloomberg articles into a knowledge graph, use that graph to retrieve grounded context, and compare the result against a pure LLM baseline and a standard vector RAG baseline.

This lets us measure whether graph structure improves:

- faithfulness of the generated answer,
- answer relevance,
- and context precision.

## Dataset

All three notebooks use the same Bloomberg Financial News 120K dataset from Hugging Face: `XJCEO/bloomberg_financial_news_120k`.

The benchmark uses the first 5,000 valid articles from the stream so that the three systems compare against the same corpus slice. The articles are streamed rather than fully loaded into memory.

### Shared benchmark split

The benchmark is organized around 20 generated questions saved to `qa_set.json` by the Pure LLM notebook. That file is then reused by both the Vanilla RAG and GraphRAG notebooks so every system answers exactly the same questions.

### Preprocessing

The article pipeline in the notebooks applies the following preprocessing steps:

- stream the Bloomberg dataset article-by-article,
- keep the first 5,000 usable articles,
- normalize article text whitespace,
- extract ticker symbols with regex for later anchoring,
- split articles into overlapping 512-character chunks with 64-character overlap,
- preserve `article_id`, `headline`, and publication date metadata for traceability.

## GraphRAG Pipeline

The GraphRAG notebook is the core of the project. It converts unstructured Bloomberg articles into a retrieval-ready knowledge graph, then uses that graph to answer finance questions with grounded context.

The notebook is split into two large phases:

1. graph construction,
2. retrieval and QA.

### Part 1: Knowledge Graph Creation

The graph construction pipeline is:

1. Stream and chunk the Bloomberg articles.
2. Run spaCy NER to extract entity mentions.
3. Use FinBERT only for token embeddings.
4. Build a Syntax-Semantics Hybrid Graph, combining:
   - dependency-based syntactic edges,
   - same-sentence co-occurrence edges,
   - embedding similarity edges.
5. Apply a two-layer GCN to propagate information across the local entity graph.
6. Extract temporal anchors and numeric facts with regex and date parsing.
7. Use Llama 3.2 3B via Ollama to extract additional relations from each chunk.
8. Write entities and relations into an in-memory `networkx.MultiDiGraph`, with optional Neo4j persistence.
9. Run Leiden community detection to form higher-level graph communities.
10. Generate short community summaries with the LLM so global retrieval has a compact semantic index.

In practice, the pipeline does three things at once:

- it keeps article-level provenance so every edge and fact can be traced back to source text,
- it creates local entity neighborhoods for question-specific retrieval,
- it creates higher-level communities for broad thematic retrieval.

### Part 2: Retrieval and QA

At inference time the notebook:

1. Classifies the question as `local`, `global`, or `mixed`.
2. Routes the question to the corresponding retriever.
3. Builds a local subgraph context, a global community-summary context, or both.
4. Sends the retrieved context to `mistral-nemo`.
5. Evaluates the answer with the RAG Triad judge prompts.

This means the notebook is not just a graph builder. It is a complete question-answering system that uses graph structure as the retrieval layer.

## Benchmark Design

The benchmark compares three notebook-backed systems built over the same Bloomberg slice and the same 20-question evaluation set.

### 1. Baseline 1: Pure LLM

Notebook: [Baseline1_PureLLM.ipynb](notebooks/ForBenchmark/Baseline1_PureLLM.ipynb)

This baseline sends each question directly to `mistral-nemo` through Ollama with no context. It is used to measure how far the model can go on parametric memory alone.

The notebook:

- generates the shared 20-question QA set with an independent judge model (`llama3.2:3b`),
- answers each question with no retrieval,
- evaluates the answers using the RAG Triad style judge prompts,
- saves results to `baseline_llm_results.json`.

### 2. Baseline 2: Vanilla RAG

Notebook: [Baseline2_VanillaRAG.ipynb](notebooks/ForBenchmark/Baseline2_VanillaRAG.ipynb)

This baseline chunks the same 5,000 articles, embeds the chunks with `all-MiniLM-L6-v2`, retrieves top-k similar chunks for each question, and answers with `mistral-nemo`.

The notebook:

- streams and chunks the same Bloomberg corpus slice,
- computes normalized sentence embeddings on CPU,
- retrieves top-5 chunks by cosine similarity,
- answers from the retrieved text only,
- evaluates with the same judge prompts,
- saves results to `baseline_rag_results.json`.

### 3. GraphRAG benchmark run

Notebook: [graph_generation.ipynb](notebooks/ForBenchmark/graph_generation.ipynb)

This is the main pipeline and the strongest benchmark candidate. It uses the graph construction flow above, then runs retrieval and QA against the shared question set.

## Technologies Employed

The notebooks and application use the following stack:

- Python
- Hugging Face `datasets`
- Hugging Face `transformers`
- PyTorch
- spaCy
- FinBERT (`ProsusAI/finbert`)
- `sentence-transformers` (`all-MiniLM-L6-v2`)
- `networkx`
- Neo4j, if available
- `python-igraph` and `leidenalg` for community detection
- `rapidfuzz` for entity grounding and validation
- Ollama for model serving
- `mistral-nemo` for answer generation
- `llama3.2:3b` for question generation, routing, summarization, and evaluation

## What Was Tested

The benchmark compares the three approaches on the same 20-question QA set and records:

- faithfulness,
- answer relevance,
- context precision,
- average triad score,
- average latency per question.

The GraphRAG notebook also logs graph statistics such as:

- number of nodes,
- number of relations,
- number of Leiden communities.

These outputs are written to `graphrag_results.json`, `baseline_rag_results.json`, and `baseline_llm_results.json` so they can be compared directly.

## Web Application Mapping

The web app is a thin interface over the same benchmark logic.

The backend exposes a query endpoint that runs the three modes side by side and returns the answers, timing, and scores. The internal modules mirror the notebook structure:

- `llm_pipeline.py` for pure LLM answering,
- `rag_pipeline.py` for chunk retrieval and vector RAG,
- `graph_pipeline.py` for graph-based retrieval.

The frontend sends a user question to the backend, displays the three answers, and lets you compare the systems in one place. In other words, the web app is not a separate experiment: it is the notebook logic wrapped as a usable comparison UI.

## Repository Layout

```
README.md
backend/
    app.py
    requirements.txt
    pipelines/
        graph_pipeline.py
        llm_pipeline.py
        rag_pipeline.py
    routes/
        query.py
frontend/
    src/
notebooks/
    ForBenchmark/
        Baseline1_PureLLM.ipynb
        Baseline2_VanillaRAG.ipynb
        graph_generation.ipynb
        qa_set.json
        baseline_llm_results.json
        baseline_rag_results.json
        graphrag_results.json
```

## How To Run

### 1. Set up Python

The notebook and backend are expected to run in the project virtual environment.

```bash
source .venv/bin/activate
```

### 2. Start Ollama

Make sure the required models are available locally.

```bash
ollama serve
```

Then pull the models used by the notebooks if needed:

```bash
ollama pull mistral-nemo
ollama pull llama3.2:3b
```

### 3. Run the notebooks

Run the notebook benchmark pipeline in this order:

1. [baseline_llm_model.ipynb](notebooks/baseline_llm_model.ipynb)
2. [rag_model.ipynb](notebooks/rag_model.ipynb)
3. [graphrag_model.ipynb](notebooks/graphrag_model.ipynb)

The first notebook generates the shared `qa_set.json`. The other two consume it.

### 4. Run the backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

The backend serves the comparison API, typically on `http://localhost:5000`.

### 5. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend typically runs on `http://localhost:5173` and calls the backend API.

If your backend runs on a different host or port, set `VITE_API_BASE_URL` accordingly.

## Configuration Notes

Environment variables are used for model and service configuration, including:

- Ollama URL,
- Neo4j connection settings,
- dataset and results paths,
- retrieval and graph thresholds.

The notebook defaults are tuned for a reproducible benchmark run, but you can reduce `process_n_chunks` in `graph_generation.ipynb` for a faster smoke test.

## Testing and Verification

The main validation comes from running the three notebooks and comparing:

- the benchmark metrics,
- the saved JSON outputs,
- the backend API response shape,
- and the frontend comparison view.

For backend-level checks:

```bash
cd backend
pytest -q
```

## Output Files

- `notebooks/ForBenchmark/qa_set.json`
- `notebooks/ForBenchmark/baseline_llm_results.json`
- `notebooks/ForBenchmark/baseline_rag_results.json`
- `notebooks/ForBenchmark/graphrag_results.json`

These files contain the benchmark questions, predictions, per-question scores, and aggregate metrics used by the comparison app.
