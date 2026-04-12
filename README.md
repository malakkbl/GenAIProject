# Financial QA Comparison Platform

Production-structured system that unifies three paradigms from the notebooks into one comparison platform:

1. Pure LLM QA (no retrieval)
2. Vanilla RAG QA (chunk + embed + top-k retrieval)
3. Graph-enhanced QA (entity/relation graph context)

## Notebook Logic Formalization

This implementation translates notebook methodology into reusable backend modules.

### Data Flow (input -> output)

- Pure LLM:
	Query -> LLM prompt -> answer -> confidence/quality score
- Vanilla RAG:
	Query -> embedding -> top-k chunk retrieval -> context-grounded prompt -> answer -> score
- Graph pipeline:
	Query -> graph context retrieval from extracted entities/relations -> graph-grounded prompt -> answer -> score

### Model and Retrieval Patterns

- LLM prompting style follows baseline notebooks:
	- role/system prompt + task-focused user prompt
	- context-injection only for RAG/Graph modes
- Embedding and chunking mirrors baseline design:
	- recursive chunking
	- configurable top-k retrieval
- Graph pipeline mirrors graph notebook design principles:
	- relation extraction patterns
	- canonical linking map
	- provenance-aware edge context

### Evaluation and Benchmarking

- All three paradigms execute in parallel for one query.
- Returned per pipeline:
	- answer
	- latency (ms)
	- quality/confidence score

## Project Structure

```
backend/
	app.py
	config/
	routes/
	services/
	pipelines/
	graph/
	retrieval/
	llm/
	evaluation/
	data/
	tests/

frontend/
	src/
```

## Backend API

### POST /query

Input:

```json
{
	"question": "What did Goldman Sachs acquire in 2022?"
}
```

Output:

```json
{
	"llm": { "answer": "...", "score": 0.73, "latency": 192.4 },
	"rag": { "answer": "...", "score": 0.81, "latency": 251.7 },
	"graph": { "answer": "...", "score": 0.79, "latency": 204.6 }
}
```

## Run Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Server starts on `http://localhost:5000`.

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173` and calls backend at `http://localhost:5000` by default.

Set `VITE_API_BASE_URL` to target a different backend URL.

## Configuration

Copy and edit environment values:

```bash
cp .env.example .env
```

The backend reads settings from environment variables (dataset size, model, retrieval, graph path, etc.).

## Testing

```bash
cd backend
pytest -q
```

Tests are isolated in `backend/tests`.
