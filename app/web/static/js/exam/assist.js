"use strict";
// The Assistant tab of a repository question: a hint ladder (no setup), or a chat with an AI model using your own
// API key, or neither. The choice is yours and is remembered. Keys are saved by the local server, never here.

const AI = {mode: store.get("oa-ai-mode", "hints"), cfg: null, busy: false, settings: false, hints: null, hintsFor: null};
const aiKey = () => R.id + ":" + R.stack + ":" + repoWS();
const aiLast = () => R.last[aiKey()];
const aiUse = (e, id) => ((e.ai = e.ai || {})[id] = e.ai[id] || {hints: 0, msgs: 0});

function aiTabHTML(){
  return `<div class="ai" id="ai"></div>`;
}

function drawAssist(){
  const box = $("#ai"); if (!box || !R.stack) return;
  const seg = [["hints", "Hints"], ["chat", "AI chat"], ["off", "Off"]].map(([k, t]) =>
    `<button data-aimode="${k}" aria-pressed="${AI.mode === k}">${t}</button>`).join("");
  box.innerHTML = `<div class="ai-head"><div class="seg" role="group" aria-label="Assistant">${seg}</div></div><div id="ai-body"></div>`;
  box.querySelectorAll("[data-aimode]").forEach(b => b.onclick = () => { AI.mode = b.dataset.aimode; store.set("oa-ai-mode", AI.mode); drawAssist(); });
  if (AI.mode === "hints") return drawHints();
  if (AI.mode === "chat") return drawChat();
  $("#ai-body").innerHTML = `<p class="muted">The assistant is off. You can turn it on at any time: <b>Hints</b> needs nothing, <b>AI chat</b> needs an API key or a model on this computer.</p>`;
}
const aiTimedNote = () => S.exam && !S.exam.practice ? `<p class="muted small">This is a test: hints and chat messages you use are listed in your report.</p>` : "";

/* ---------- hints ---------- */
function drawHints(){
  const body = $("#ai-body"), res = aiLast();
  if (!res){
    body.innerHTML = `<p>Hints are for the tests that fail. Run the tests first.</p><button class="btn" id="ai-run">Run tests</button>` + aiTimedNote();
    $("#ai-run").onclick = () => repoRun(false);
    return;
  }
  const failing = res.tests.filter(t => !t.ok && !t.hidden).map(t => t.id);
  if (!failing.length){
    body.innerHTML = `<p class="ok-line">Every visible test passes. ${res.full ? "" : "Submit to run the hidden tests as well."}</p>`
      + `<p class="muted small">Hidden tests get no hints: the README's rules are what they check.</p>`;
    return;
  }
  const want = aiKey() + "|" + failing.join(",");
  if (AI.hintsFor !== want){
    body.innerHTML = `<p class="muted">Loading hints…</p>`;
    rapi(repoURL(R.id, R.stack, "hints"), {failing}).then(h => { AI.hints = h; AI.hintsFor = want; drawHints(); })
      .catch(err => { body.innerHTML = `<p class="muted">${esc(err.message)}</p>`; });
    return;
  }
  const e = S.exam, seen = (e.aiSeen = e.aiSeen || {})[aiKey()] = e.aiSeen[aiKey()] || {};
  const label = ["Where to look", "What's wrong", "How to fix it"];
  const tests = AI.hints.tests.map(t => {
    const bugs = t.bugs.length ? t.bugs.map((steps, i) => {
      const k = t.id + "#" + i, n = seen[k] || 0;
      const shown = steps.slice(0, n).map((s, j) => `<li><span class="hl">${label[j]}</span>${mdInline(s)}</li>`).join("");
      return `<ol class="ladder">${shown}</ol>${n < steps.length ? `<button class="btn sm" data-hint="${esc(k)}">${n ? "Next hint" : "Show a hint"}: ${label[n].toLowerCase()}</button>` : ""}`;
    }).join(t.bugs.length > 1 ? `<p class="muted small">This test has another cause too:</p>` : "")
      : `<p class="muted small">No planted bug is behind this test. Check what you changed, or read the error in Tests.</p>`;
    return `<li class="hint-test"><div class="ht">${esc(t.title)}</div>${bugs}</li>`;
  }).join("");
  body.innerHTML = `<p class="muted small">${failing.length} visible test${failing.length === 1 ? "" : "s"} failing. Each hint goes one step further: try the first before asking for the next.</p><ul class="hints">${tests}</ul>` + aiTimedNote();
  body.querySelectorAll("[data-hint]").forEach(b => b.onclick = () => {
    seen[b.dataset.hint] = (seen[b.dataset.hint] || 0) + 1; aiUse(e, R.id).hints++; saveExam(); drawHints();
  });
}
// The hints are short Markdown: only `code` and **bold**.
const mdInline = s => esc(s).replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>");

/* ---------- chat ---------- */
function aiLoad(){ return AI.cfg ? Promise.resolve(AI.cfg) : rapi("/api/assist").then(c => (AI.cfg = c)); }
const aiChatMode = () => store.get("oa-ai-help", "coach");
function aiMessages(){ const e = S.exam, all = (e.aiChat = e.aiChat || {}); return (all[aiKey()] = all[aiKey()] || []); }

function drawChat(){
  const body = $("#ai-body");
  body.innerHTML = `<p class="muted">Loading…</p>`;
  aiLoad().then(cfg => {
    const p = cfg.provider && cfg.providers[cfg.provider];
    if (AI.settings || !p || !p.has_key) return drawSettings(cfg);
    const msgs = aiMessages();
    const starters = ["Where should I start?", "Explain the first failing test", "I changed something; is it right?"];
    body.innerHTML = `<div class="ai-bar"><span class="muted small">${esc(p.name)} · <code>${esc(p.model)}</code> · ${aiChatMode() === "full" ? "full help" : "coach"}</span><div class="spacer"></div>
        <button class="linkbtn" id="ai-set">Settings</button>${msgs.length ? `<button class="linkbtn" id="ai-clear">Clear</button>` : ""}</div>
      <div class="chat" id="chat" aria-live="polite">${msgs.length ? msgs.map(msgHTML).join("") : `<div class="chat-empty"><p class="muted">Ask about the code, a failing test or an error. It sees the question, the README, your current files and the latest test results.</p><div class="starters">${starters.map(s => `<button class="starter" data-start="${esc(s)}">${esc(s)}</button>`).join("")}</div></div>`}</div>
      <form class="composer" id="composer"><textarea id="ai-in" rows="2" placeholder="Ask the assistant… (Enter to send, Shift+Enter for a new line)" aria-label="Message"></textarea><button class="btn primary" id="ai-send">Send</button></form>` + aiTimedNote();
    $("#ai-set").onclick = () => { AI.settings = true; drawChat(); };
    const c = $("#ai-clear"); if (c) c.onclick = () => { aiMessages().length = 0; saveExam(); drawChat(); };
    body.querySelectorAll("[data-start]").forEach(b => b.onclick = () => send(b.dataset.start));
    const ta = $("#ai-in");
    ta.addEventListener("keydown", ev => { if (ev.key === "Enter" && !ev.shiftKey && !ev.metaKey && !ev.ctrlKey){ ev.preventDefault(); send(ta.value); } ev.stopPropagation(); });
    $("#composer").onsubmit = ev => { ev.preventDefault(); send(ta.value); };
    scrollChat();
    if (AI.busy) busyLine(true);
  }).catch(err => { body.innerHTML = `<p class="muted">${esc(err.message)}</p>`; });
}
function msgHTML(m){
  if (m.role === "user") return `<div class="msg-u">${esc(m.content).replace(/\n/g, "<br>")}</div>`;
  if (m.role === "error") return `<div class="msg-err">${esc(m.content)}</div>`;
  return `<div class="msg-a md">${mdHTML(m.content)}</div>`;
}
function scrollChat(){ const c = $("#chat"); if (c) c.scrollTop = c.scrollHeight; }
function busyLine(on){
  const c = $("#chat"); if (!c) return;
  const old = $("#ai-busy"); if (old) old.remove();
  if (on){ c.insertAdjacentHTML("beforeend", `<div class="msg-busy" id="ai-busy"><span class="oi-spin" aria-hidden="true"></span>Thinking…</div>`); scrollChat(); }
  const s = $("#ai-send"); if (s) s.disabled = on;
}
// The latest test run, as text for the model: only what the learner can see.
function aiResults(){
  const r = aiLast(); if (!r) return "No test run yet.";
  const lines = [`${r.full ? "Submit" : "Run"}: ${r.passed} of ${r.total} tests passed.`];
  r.tests.forEach(t => { if (!t.hidden) lines.push(`${t.ok ? "PASS" : "FAIL"} ${t.title} (${t.name})` + (t.ok ? "" : "\n    " + String(t.message || "").slice(0, 1500).replace(/\n/g, "\n    "))); });
  const hiddenFails = r.tests.filter(t => t.hidden && !t.ok).length; if (hiddenFails) lines.push(`${hiddenFails} hidden test(s) failed (no details are shown for hidden tests).`);
  return lines.join("\n");
}
function send(text){
  text = String(text || "").trim(); if (!text || AI.busy) return;
  const e = S.exam, key = aiKey(), list = aiMessages(), id = R.id, stack = R.stack;
  list.push({role: "user", content: text}); aiUse(e, id).msgs++;
  while (list.length > 40) list.shift();
  saveExam(); AI.busy = true; drawChat();
  repoFlush().then(() => rapi(repoURL(id, stack, "chat"), {messages: list.filter(m => m.role !== "error").map(({role, content}) => ({role, content})),
    mode: aiChatMode(), file: R.cur || "", results: aiResults()}))
    .then(r => { list.push({role: "assistant", content: r.text}); })
    .catch(err => { list.push({role: "error", content: err.message}); })
    .finally(() => { AI.busy = false; saveExam(); if (aiKey() === key && AI.mode === "chat" && $("#ai")) drawChat(); });
}

/* ---------- settings ---------- */
function drawSettings(cfg){
  const body = $("#ai-body");
  let cur = cfg.provider || "anthropic";
  const draw = () => {
    const p = cfg.providers[cur];
    body.innerHTML = `<form class="ai-set" id="ai-form">
      <p>Chat with an AI model about this repository, like the assistant in an AI-assisted OA. Use your own API key, or a model running on this computer with Ollama.</p>
      <label class="field">Provider<select id="ai-prov">${Object.entries(cfg.providers).map(([k, v]) => `<option value="${k}" ${k === cur ? "selected" : ""}>${esc(v.name)}${v.has_key && !v.nokey ? " · key saved" : ""}</option>`).join("")}</select></label>
      ${p.nokey ? `<p class="muted small">Needs <a href="${p.keys}" target="_blank" rel="noopener">Ollama</a> running, with the model pulled (<code>ollama pull ${esc(p.model)}</code>).</p>`
        : `<label class="field">API key<input id="ai-key" type="password" autocomplete="off" spellcheck="false" placeholder="${p.has_key ? "Saved (ends in " + esc(p.key_end || "…") + "). Paste a new one to replace it" : "Paste your key"}"></label>
           <p class="muted small"><a href="${p.keys}" target="_blank" rel="noopener">Get a key</a>. It is saved only on this computer, in <code>.oa-cache/assistant.json</code>, and sent only to ${esc(p.name.split(" (")[0])}. Usage is billed to your account by the provider.</p>`}
      <label class="field">Model<span class="row"><input id="ai-model" list="ai-models" value="${esc(p.model)}" spellcheck="false"><button type="button" class="btn sm" id="ai-load" ${p.has_key ? "" : "disabled"} title="Ask the provider which models it has">Load models</button></span></label>
      <datalist id="ai-models">${p.suggest.map(m => `<option value="${esc(m)}">`).join("")}</datalist>
      <fieldset class="field"><legend>How it helps</legend>
        <label class="radio"><input type="radio" name="ai-help" value="coach" ${aiChatMode() !== "full" ? "checked" : ""}><span><b>Coach</b>: points you to the problem and explains, but doesn't write the fix</span></label>
        <label class="radio"><input type="radio" name="ai-help" value="full" ${aiChatMode() === "full" ? "checked" : ""}><span><b>Full help</b>: answers like the real OA's assistant, fixes included</span></label></fieldset>
      <details class="adv"><summary>Address</summary><label class="field">Chat completions URL<input id="ai-url" value="${esc(p.url)}" spellcheck="false"></label>
        <p class="muted small">Change it for a compatible server (a proxy, LM Studio, another Ollama port). Default: <code>${esc(p.default_url)}</code></p></details>
      <div class="oi-row">${p.has_key && !p.nokey ? `<button type="button" class="linkbtn rm" id="ai-forget">Forget this key</button>` : ""}<div class="spacer"></div>
        ${cfg.provider && cfg.providers[cfg.provider].has_key ? `<button type="button" class="btn" id="ai-cancel">Cancel</button>` : ""}<button class="btn primary">Save</button></div>
      <p class="small" id="ai-msg" aria-live="polite"></p></form>`;
    $("#ai-prov").onchange = ev => { cur = ev.target.value; draw(); };
    const msg = t => { $("#ai-msg").textContent = t; };
    $("#ai-load").onclick = () => { msg("Asking for the model list…");
      rapi("/api/assist", {action: "models", provider: cur}).then(r => { $("#ai-models").innerHTML = r.models.map(m => `<option value="${esc(m)}">`).join(""); msg(r.models.length + " models: click the Model box to pick one."); })
        .catch(err => msg(err.message)); };
    const f = $("#ai-forget"); if (f) f.onclick = () => rapi("/api/assist", {provider: cur, key: "", forget: true, use: false}).then(c => { AI.cfg = cfg = c; draw(); });
    const cn = $("#ai-cancel"); if (cn) cn.onclick = () => { AI.settings = false; drawChat(); };
    $("#ai-form").onsubmit = ev => {
      ev.preventDefault();
      const k = $("#ai-key"), help = body.querySelector('[name="ai-help"]:checked');
      if (help) store.set("oa-ai-help", help.value);
      const req = {provider: cur, model: $("#ai-model").value, url: $("#ai-url").value === p.default_url ? "" : $("#ai-url").value};
      if (k && k.value.trim()) req.key = k.value.trim();
      if (!p.has_key && !p.nokey && !req.key){ msg("Paste an API key first."); return; }
      msg("Saving…");
      rapi("/api/assist", req).then(c => { AI.cfg = c; AI.settings = false; drawChat(); }).catch(err => msg(err.message));
    };
  };
  draw();
}

// The test results changed: hints follow the failing tests.
function assistAfterRun(){ if (AI.mode === "hints" && $("#ai") && !$("#doc-ai").hidden) drawHints(); }
