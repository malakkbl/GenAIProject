import { useState } from "react";

export default function ChatInput({ onSubmit, loading }) {
  const [question, setQuestion] = useState("");

  const submit = (event) => {
    event.preventDefault();
    const clean = question.trim();
    if (!clean || loading) return;
    onSubmit(clean);
  };

  return (
    <form className="chat-form" onSubmit={submit}>
      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        className="chat-input"
        placeholder="Ask a financial-news question to compare Pure LLM, Vanilla RAG, and Graph pipelines..."
        rows={3}
      />
      <button type="submit" className="send-btn" disabled={loading}>
        {loading ? "Running..." : "Compare"}
      </button>
    </form>
  );
}
