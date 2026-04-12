import ScoreBadge from "./ScoreBadge";

export default function ComparisonPanel({ title, payload, loading }) {
  return (
    <section className="panel">
      <header className="panel-head">
        <h2>{title}</h2>
      </header>
      {loading ? (
        <p className="panel-loading">Generating answer...</p>
      ) : payload ? (
        <>
          <ScoreBadge score={payload.score} latency={payload.latency} />
          <p className="answer-text">{payload.answer}</p>
        </>
      ) : (
        <p className="panel-empty">No response yet.</p>
      )}
    </section>
  );
}
