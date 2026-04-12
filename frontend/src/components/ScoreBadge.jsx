export default function ScoreBadge({ score, latency }) {
  const numericScore = typeof score === "number" ? score : 0;
  const latencyMs = typeof latency === "number" ? latency : 0;

  return (
    <div className="score-row">
      <span className="score-pill">Score {numericScore.toFixed(3)}</span>
      <span className="latency-pill">{latencyMs.toFixed(1)} ms</span>
    </div>
  );
}
