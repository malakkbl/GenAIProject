# GraphRAG for Social Sciences

## Team
- Malak Kably
- Safae Hajjout

---

## Step 1: Dataset Selection

We selected the following dataset for our project:

- **Dataset**: Bloomberg Financial News (120K articles)  
- **Source**: https://huggingface.co/datasets/XJCEO/bloomberg_financial_news_120k 

### Why this dataset?
- Contains large-scale **financial and economic news**
- Rich in **entities (companies, policies, markets)**
- Suitable for **knowledge graph construction and reasoning**

---

## Step 2: Project Scope

### Domain
Financial and Economic News

### Context
We aim to build a system that can understand and reason over financial news articles by extracting structured knowledge and using it to answer complex questions.

### Problem Statement
Build a **GraphRAG-based system** that:
- Extracts entities and relationships from financial news
- Constructs a knowledge graph
- Uses graph-based retrieval to improve LLM question answering
- Enables **multi-hop reasoning over economic events and entities**

---

## Step 3: Literature Review

### GraphRAG Overview
GraphRAG extends traditional RAG by incorporating **knowledge graphs** to structure and retrieve information more effectively.

Instead of retrieving flat text chunks:
- It retrieves **connected knowledge**
- Enables **multi-hop reasoning**
- Improves **explainability**

---

### Key Ideas
- Combine:
  - LLMs (generation)
  - Knowledge Graphs (structure)
  - Retrieval (context selection)

- Pipeline:
Documents → Entities/Relations → Knowledge Graph → Graph Retrieval → LLM

