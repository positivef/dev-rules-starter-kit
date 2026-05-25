"""Render the model dict into a single self-contained HTML file."""

from __future__ import annotations

import json

_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Session Workflow Dashboard</title>
<style>
:root{color-scheme:dark}
body{font-family:-apple-system,Segoe UI,Roboto,sans-serif;margin:0;
background:#0d1117;color:#e6edf3;padding:24px}
h1{font-size:20px;margin:0 0 4px}
.meta{color:#8b949e;font-size:12px;margin-bottom:20px}
.project{border:1px solid #30363d;border-radius:10px;padding:16px;margin-bottom:20px}
.project h2{margin:0 0 8px;font-size:16px}
.git{font-size:13px;color:#8b949e;margin-bottom:12px}
.git b{color:#e6edf3}
table{width:100%;border-collapse:collapse;margin:8px 0 16px;font-size:13px}
th,td{text-align:left;padding:6px 8px;border-bottom:1px solid #21262d}
th{color:#8b949e;font-weight:600}
.live{color:#3fb950;font-weight:600}
.badge{display:inline-block;padding:1px 7px;border-radius:10px;font-size:11px}
.in-progress{background:#1f6feb33;color:#79c0ff}
.paused{background:#9e6a0322;color:#e3b341}
.idle{background:#30363d;color:#8b949e}
.conflicts{margin:0 0 8px}
.c{padding:8px 12px;border-radius:8px;margin:6px 0;font-size:13px}
.c.red{background:#da363322;border:1px solid #da3633}
.c.warn{background:#9e6a0322;border:1px solid #bb8009}
.c.yellow{background:#9e6a0314;border:1px solid #54600c}
.none{color:#3fb950;font-size:13px}
.section-label{font-size:12px;color:#8b949e;text-transform:uppercase;
letter-spacing:.5px;margin-top:8px}
</style>
</head>
<body>
<h1>Session Workflow Dashboard</h1>
<div class="meta" id="meta"></div>
<div id="root"></div>
<script>
const MODEL = __MODEL__;
const SEV = {red:"\\u{1F534}", warn:"\\u26A0\\uFE0F", yellow:"\\u{1F7E1}"};
function esc(s){return (s==null?"":String(s)).replace(/[&<>]/g,
  c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));}
function render(){
  const m=MODEL;
  document.getElementById("meta").textContent=
    "generated "+m.generated_at+"  |  freshness "+m.config.freshness_minutes+
    "min, stale "+m.config.stale_days+"d";
  const root=document.getElementById("root");
  root.innerHTML=m.projects.map(p=>{
    const conflicts = p.conflicts.length
      ? p.conflicts.map(c=>`<div class="c ${esc(c.severity)}">`+
          `${SEV[c.severity]||""} <b>${esc(c.rule)}</b> &mdash; ${esc(c.detail)}</div>`).join("")
      : `<div class="none">\\u2705 no tangles detected</div>`;
    const slots = p.slots.map(s=>`<tr>`+
      `<td>${esc(s.slot)}</td>`+
      `<td><span class="badge ${esc(s.status)}">${esc(s.status)}</span></td>`+
      `<td>${esc(s.topic)||"<i>&mdash;</i>"}</td>`+
      `<td>${esc((s.last_updated||"").slice(0,16))}</td></tr>`).join("");
    const sessions = p.sessions.map(s=>`<tr>`+
      `<td>${esc(s.id_short)}</td>`+
      `<td>${s.live?'<span class="live">live</span>':""}</td>`+
      `<td>${esc(s.title)||"<i>&mdash;</i>"}</td>`+
      `<td>${esc(s.branch)||"<i>&mdash;</i>"}</td>`+
      `<td>${esc((s.last_activity||"").slice(0,16))}</td>`+
      `<td>${s.pr?("#"+esc(s.pr)):""}</td></tr>`).join("");
    const g=p.git;
    return `<div class="project">
      <h2>${esc(p.name)}</h2>
      <div class="git">branch <b>${esc(g.branch)}</b> &middot;
        <b>${g.uncommitted}</b> uncommitted &middot;
        <b>${g.unpushed}</b> unpushed &middot;
        <b>${g.commits_24h}</b> commits/24h &middot;
        worktrees: ${esc((g.worktrees||[]).join(", "))||"&mdash;"}</div>
      <div class="conflicts">${conflicts}</div>
      <div class="section-label">Slots (coordination)</div>
      <table><tr><th>slot</th><th>status</th><th>topic</th><th>updated</th></tr>
        ${slots||'<tr><td colspan=4><i>none</i></td></tr>'}</table>
      <div class="section-label">Sessions (recent)</div>
      <table><tr><th>id</th><th></th><th>title</th><th>branch</th>
        <th>last activity</th><th>pr</th></tr>
        ${sessions||'<tr><td colspan=6><i>none</i></td></tr>'}</table>
    </div>`;
  }).join("");
}
render();
</script>
</body>
</html>
"""


def render_html(model: dict) -> str:
    data = json.dumps(model, ensure_ascii=False).replace("</", "<\\/")
    return _TEMPLATE.replace("__MODEL__", data)
