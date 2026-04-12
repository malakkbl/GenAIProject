const API_BASE = "http://localhost:5000";
let currentResults = null;

const $ = id => document.getElementById(id);

// ── Health check ──────────────────────────────────────────
async function checkBackend() {
  try {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(3000) });
    if (res.ok) { setStatus("ok", "Backend ready"); }
    else         { throw new Error(); }
  } catch { setStatus("error", "Backend offline"); }
}
checkBackend();

function setStatus(cls, label) {
  $("status-dot").className = "foot-dot " + cls;
  $("status-label").textContent = label;
}

// ── Submit on Ctrl+Enter ──────────────────────────────────
$("question-input").addEventListener("keydown", e => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") runQuery();
});

// ── Auto-resize textarea ──────────────────────────────────
$("question-input").addEventListener("input", function () {
  this.style.height = "auto";
  this.style.height = this.scrollHeight + "px";
});

// ── Query ─────────────────────────────────────────────────
async function runQuery() {
  const question = $("question-input").value.trim();
  if (!question) return;

  setLoading(true);
  reset();
  skeletons(true);

  try {
    const res = await fetch(`${API_BASE}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    if (!res.ok) throw new Error((await res.json().catch(()=>({}))).error || `Error ${res.status}`);

    const data = await res.json();
    currentResults = data;

    $("q-text").textContent = question;
    $("question-echo").classList.remove("hidden");

    skeletons(false);
    render("llm",   data.llm);
    render("rag",   data.rag);
    render("graph", data.graph);
    setStatus("ok", "Backend ready");
    $("error-msg").classList.add("hidden");

  } catch (err) {
    skeletons(false);
    $("error-msg").textContent = err.message.includes("fetch")
      ? "Cannot reach backend — is it running? Open start_backend.bat"
      : err.message;
    $("error-msg").classList.remove("hidden");
    setStatus("error", "Backend offline");
  } finally {
    setLoading(false);
  }
}

// ── Render one panel ──────────────────────────────────────
function render(key, payload) {
  if (!payload) return;

  $("ans-" + key).textContent = payload.answer || "(no answer)";

  const score = typeof payload.score === "number" ? payload.score : 0;
  setTimeout(() => { $("bar-" + key).style.width = Math.round(score * 100) + "%"; }, 60);
  $("score-" + key).textContent = score.toFixed(2);

  if (payload.latency) {
    $("lat-" + key).textContent = (payload.latency / 1000).toFixed(2) + "s";
  }

  if (key === "rag" && payload.metadata?.retrieved_article_ids?.length) {
    const ids = payload.metadata.retrieved_article_ids;
    const src = $("sources-rag");
    src.innerHTML = ids.map(id => `<span class="source-chip">#${id}</span>`).join("");
    src.classList.remove("hidden");
    $("ret-rag").textContent = ids.length + " chunks";
  }

  if (key === "graph" && payload.metadata?.context_preview) {
    const ctx = $("ctx-graph");
    ctx.textContent = payload.metadata.context_preview;
    ctx.classList.remove("hidden");
  }
}

// ── Select ────────────────────────────────────────────────
function selectAnswer(key) {
  if (!currentResults?.[key]) return;
  const names = { llm: "Pure LLM", rag: "Vanilla RAG", graph: "GraphRAG" };

  ["llm","rag","graph"].forEach(k => {
    $("panel-" + k).classList.toggle("selected", k === key);
    const b = $("sel-" + k);
    b.classList.toggle("active", k === key);
    b.textContent = k === key ? "Selected" : "Select";
  });

  $("sel-tag").textContent = names[key];
  $("selected-answer").textContent = currentResults[key].answer || "";
  $("selected-section").classList.remove("hidden");
  $("selected-section").scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// ── Copy ──────────────────────────────────────────────────
async function copySelected() {
  const text = $("selected-answer").textContent;
  try { await navigator.clipboard.writeText(text); }
  catch { const t=document.createElement("textarea");t.value=text;document.body.appendChild(t);t.select();document.execCommand("copy");document.body.removeChild(t); }
  const b = document.querySelector(".copy-btn");
  b.textContent = "Copied";
  setTimeout(() => { b.textContent = "Copy"; }, 1800);
}

// ── Helpers ───────────────────────────────────────────────
function setLoading(on) {
  $("ask-btn").disabled = on;
  $("btn-label").classList.toggle("hidden", on);
  $("btn-spinner").classList.toggle("hidden", !on);
}

function skeletons(on) {
  ["llm","rag","graph"].forEach(k => $("skel-" + k).classList.toggle("hidden", !on));
}

function reset() {
  $("selected-section").classList.add("hidden");
  $("question-echo").classList.add("hidden");
  ["llm","rag","graph"].forEach(k => {
    $("ans-"   + k).textContent = "";
    $("bar-"   + k).style.width = "0%";
    $("score-" + k).textContent = "-";
    $("lat-"   + k).textContent = "";
    $("panel-" + k).classList.remove("selected");
    const b = $("sel-" + k);
    b.classList.remove("active");
    b.textContent = "Select";
  });
  const src = $("sources-rag");
  src.innerHTML = ""; src.classList.add("hidden");
  $("ret-rag").textContent = "";
  const ctx = $("ctx-graph");
  ctx.textContent = ""; ctx.classList.add("hidden");
}
