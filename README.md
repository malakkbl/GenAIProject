# GraphRAG for Financial News
**Team**: Malak Kably, Safae Hajjout
**Dataset**: Bloomberg Financial News 120K — `Headline`, `Article`, `Date`, `Journalists`, `Link`

---

## Pipeline

| # | Phase | Status | Output |
|---|-------|--------|--------|
| 1 | Dataset Selection | ✅ | Bloomberg 120K chosen |
| 2 | Literature Review | 🔄 | Papers on GraphRAG, entity/relation extraction |
| 3 | Entity & Relation Extraction | ⬜ | Triples: `(entity1, relation, entity2)` |
| 4 | Knowledge Graph Construction | ⬜ | Graph: nodes = entities, edges = relations |
| 5 | GraphRAG Retrieval | ⬜ | Subgraph + text chunks per query |
| 6 | LLM Integration | ⬜ | Answers from graph context |
| 7 | Evaluation | ⬜ | GraphRAG vs RAG vs LLM-only |
| 8 | Demo | ⬜ | Streamlit/Gradio interface |

---

## Key Decisions

| What | Choice |
|------|--------|
| Entity extraction | spaCy NER |
| Relation extraction | LLM-based prompting (regex failed in exploration) |
| Graph library | NetworkX (prototype) → Neo4j (scale) |
| LLM | Claude API |
| Evaluation | Accuracy + faithfulness on curated Q&A pairs |

---

## Files
- [Dataset_Exploration.ipynb](Dataset_Exploration.ipynb) — Phase 1
- [EntityExtractionPapers/](EntityExtractionPapers/) — Phase 2
