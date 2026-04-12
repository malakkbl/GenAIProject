from __future__ import annotations


def llm_only_system_prompt() -> str:
    return (
        "You are a knowledgeable financial analyst. "
        "Answer clearly and concisely in 2-4 sentences."
    )


def rag_system_prompt() -> str:
    return (
        "You are a knowledgeable financial analyst with access to retrieved Bloomberg context. "
        "Ground the answer in provided context. If context is insufficient, say so."
    )


def graph_system_prompt() -> str:
    return (
        "You are a financial knowledge-graph assistant. "
        "Use only graph context and provenance snippets."
    )


def build_rag_user_prompt(question: str, retrieved_chunks: list[dict]) -> str:
    context_lines = []
    for idx, chunk in enumerate(retrieved_chunks, start=1):
        context_lines.append(
            f"[Source {idx} | Article {chunk['article_id']} | Similarity {chunk['score']:.3f}]\n"
            f"{chunk['text']}"
        )
    context_block = "\n\n".join(context_lines)
    return (
        "Retrieved context from Bloomberg Financial News:\n\n"
        f"{context_block}\n\n"
        f"Question: {question}\n\n"
        "Answer based on the context above:"
    )


def build_graph_user_prompt(question: str, graph_context: str) -> str:
    return (
        "Knowledge graph context:\n"
        f"{graph_context}\n\n"
        f"Question: {question}\n\n"
        "Answer only from graph context. If insufficient, state that explicitly."
    )
