import { useState } from "react";
import ChatInput from "./components/ChatInput";
import ComparisonPanel from "./components/ComparisonPanel";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";

export default function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [lastQuestion, setLastQuestion] = useState("");

  const runQuery = async (question) => {
    setLoading(true);
    setError("");
    setLastQuestion(question);
    try {
      const response = await fetch(`${API_BASE}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      if (!response.ok) {
        throw new Error(`Request failed (${response.status})`);
      }
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page">
      <section className="hero">
        <p className="kicker">Financial QA Platform</p>
        <h1>Compare Pure LLM vs Vanilla RAG vs Graph Pipeline</h1>
        <p className="subtitle">
          One question, three paradigms, side-by-side evidence of retrieval strategy impact.
        </p>
      </section>

      <ChatInput onSubmit={runQuery} loading={loading} />

      {lastQuestion && <p className="question-line">Question: {lastQuestion}</p>}
      {error && <p className="error-banner">{error}</p>}

      <section className="panel-grid">
        <ComparisonPanel title="Pure LLM" payload={result?.llm} loading={loading} />
        <ComparisonPanel title="Vanilla RAG" payload={result?.rag} loading={loading} />
        <ComparisonPanel title="Graph Pipeline" payload={result?.graph} loading={loading} />
      </section>
    </main>
  );
}
