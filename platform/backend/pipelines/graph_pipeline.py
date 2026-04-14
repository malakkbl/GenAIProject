"""
GraphRAG pipeline.

Replace the body of run_graph() with your actual pipeline logic.
The function must return a dict with these keys:
  - answer   (str)   the generated answer
  - score    (float) quality score between 0 and 1
  - latency  (float) time in milliseconds
  - metadata (dict)  optional — the UI will show context_preview if present
                     e.g. {"context_preview": "(Marriott) --[HOLDS_POSITION]--> (Arne Sorenson)"}
"""

import time


def run_graph(question: str) -> dict:
    t0 = time.perf_counter()

    # ── Replace everything below this line with your real GraphRAG logic ─────
    answer = (
        "Based on the knowledge graph analysis of Bloomberg financial news, major acquisitions reveal: "
        "Microsoft (ORG) --[ACQUIRED]--> Activision Blizzard (ORG) | CEO: Bobby Kotick (PERSON) moved to advisory role; "
        "Market Impact: Gaming & Entertainment sector volatility increased 12%. "
        "Broadcom (ORG) --[ACQUIRED]--> VMware (ORG) | CEO: Raghu Raghuram (PERSON) --[LEADS]--> Broadcom; "
        "Market Impact: Enterprise Software sector saw consolidation wave. "
        "Tesla (ORG) --[LED_BY]--> Elon Musk (PERSON) --[DIRECTED]--> Strategic Expansion (EVENT); "
        "Impact Indicators: Stock volatility, regulatory scrutiny, competitive positioning. "
        "These multi-hop relationships show interconnected market dynamics across sectors."
    )
    score = 0.84
    metadata = {
        "context_preview": (
            "(Microsoft) --[ACQUIRED]--> (Activision Blizzard)\n"
            "(Bobby Kotick) --[WAS_CEO_OF]--> (Activision Blizzard)\n"
            "(Activision Blizzard) --[OPERATES_IN]--> (Gaming Sector)\n\n"
            "(Broadcom) --[ACQUIRED]--> (VMware)\n"
            "(Raghu Raghuram) --[CEO_OF]--> (Broadcom)\n"
            "(VMware) --[OPERATES_IN]--> (Enterprise Software)\n\n"
            "(Elon Musk) --[LEADS]--> (Tesla)\n"
            "(Tesla) --[ANNOUNCED]--> (Strategic Expansion)\n"
            "(Expansion) --[IMPACTS]--> (Market Valuation)"
        ),
        "retrieved_article_ids": [12, 45, 89, 156, 203],
        "graph_depth": "3-hop relationships",
    }
    # ────────────────────────────────────────────────────────────────────────

    latency = (time.perf_counter() - t0) * 1000
    return {
        "answer":   answer,
        "score":    round(score, 3),
        "latency":  round(latency, 2),
        "metadata": metadata,
    }
