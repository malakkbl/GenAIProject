# GraphRAG Platform

## Where to put this folder

Place `platform/` inside your existing `Repository/`:

```
Repository/
  notebooks/
  platform/        ← here
    backend/
    frontend/
    setup.bat
    start_backend.bat
    README.md
```

---

## Setup (once)

**Step 1 — Create a virtual environment** (avoids Windows permission errors):

```bat
cd platform\backend
python -m venv venv
venv\Scripts\activate
```

**Step 2 — Install dependencies:**

```bat
pip install -r requirements.txt
```

Only two packages install: `flask` and `flask-cors`. Done in seconds.

---

## Run

**Every time you want to start the platform:**

```bat
cd platform\backend
venv\Scripts\activate
python app.py
```

Then open `frontend/index.html` in your browser.  
The status dot at the bottom of the page turns green when the backend is reachable.

> You can also double-click `start_backend.bat` — but make sure the venv is activated first, or run it from inside the activated terminal.

---

## Connecting your pipelines

Each pipeline is one file with one function. Fill in the section marked between the comment lines:

| Pipeline    | File                                | Function    |
|-------------|-------------------------------------|-------------|
| Pure LLM    | `backend/pipelines/llm_pipeline.py`   | `run_llm()`   |
| Vanilla RAG | `backend/pipelines/rag_pipeline.py`   | `run_rag()`   |
| GraphRAG    | `backend/pipelines/graph_pipeline.py` | `run_graph()` |

Each function receives the question as a string and must return:

```python
{
    "answer":  "...",   # str
    "score":   0.85,    # float 0-1
    "latency": 1234.0,  # milliseconds — use time.perf_counter()
    "metadata": {}      # optional dict
}
```

Nothing else in the codebase needs to change when you update a pipeline.