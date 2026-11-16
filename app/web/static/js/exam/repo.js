"use strict";
// Repository questions: a small IDE for a real project (file tree, tabs, README, Run tests / Submit), and the
// environments it runs in (Django today; Node.js and Spring Boot next). The server side is app/server/repos.py
// and app/server/envs.py.

const ENV_ORDER = ["node", "django", "spring"];
const ENV_FALLBACK = {   // shown for stacks this question doesn't have yet
  node: {name: "Node.js · Express (MERN)", short: "Node.js", lang: "JavaScript"},
  django: {name: "Python · Django", short: "Django", lang: "Python"},
  spring: {name: "Java · Spring Boot", short: "Spring Boot", lang: "Java"},
};
const R = {id: null, stack: null, tree: null, docs: {}, open: [], cur: null, dirty: new Set(), timers: {}, envs: null,
  last: {}, tab: "tests", busy: false, poll: null};

const rapi = (path, body) => fetch(path, body ? {method: "POST", headers: {"Content-Type": "application/json", "X-Token": window.LOCAL_TOKEN || ""}, body: JSON.stringify(body)}
  : {headers: {"X-Token": window.LOCAL_TOKEN || ""}}).then(r => r.json().catch(() => ({})).then(j => { if (!r.ok) throw new Error(j.error || "the app answered " + r.status); return j; }));
// practice keeps one copy of each repository; every timed test starts from a fresh copy of its own
const repoWS = () => S.exam && !S.exam.practice ? "t" + S.exam.start : "practice";
const repoURL = (id, stack, what, params) => `/api/repos/${encodeURIComponent(window.OA_COMPANY)}/${encodeURIComponent(id)}/${stack}/${what}?`
  + new URLSearchParams(Object.assign(what === "solution" ? {} : {ws: repoWS()}, params || {}));
const envInfo = k => (R.envs && R.envs.envs[k]) || ENV_FALLBACK[k];
const envName = k => (envInfo(k) || {}).name || k;
const repoStacks = q => q.stacks || [];
const lockedEnv = (e, id) => !e.practice && e.lang[id] && (e.envLock || {})[id];

/* ---------- markup ---------- */
function repoHTML(q, e){
  const stack = e.lang[q.id];
  const tags = qTags(q).map(t => `<span class="tag">${esc(String(t))}</span>`).join("");
  return `
  <div class="exam repo-exam">
    <article class="stmt" id="stmt">
      <div class="meta"><span class="pill d-${q.diff}">${q.diff === "Repo" ? "Repository" : q.diff}</span>${tags}<span>${esc(q.src)}</span></div>
      <h2>${esc(q.title)}</h2>
      <div class="doc-tabs" role="tablist" aria-label="Question and README">
        <button role="tab" data-doc="q" aria-selected="true">Question</button>
        <button role="tab" data-doc="readme" aria-selected="false" ${stack ? "" : "disabled"}>README.md</button>
        <button role="tab" data-doc="ai" aria-selected="false" ${stack ? "" : "disabled"}>Assistant</button>
      </div>
      <div class="doc" id="doc-q">${q.body}</div>
      <div class="doc md" id="doc-readme" hidden></div>
      <div class="doc" id="doc-ai" hidden>${aiTabHTML()}</div>
    </article>
    <div class="rz-v" id="rz-v" role="separator" aria-orientation="vertical" aria-label="Resize the question panel" tabindex="0"></div>
    <section class="work repo-work" aria-label="Repository">
      <div class="toolbar">
        <button class="env-btn" id="env-btn" aria-haspopup="true" aria-expanded="false" ${stack ? "" : "hidden"}>
          <span class="env-dot" aria-hidden="true"></span><span id="env-name">${stack ? esc(envInfo(stack).short || stack) : ""}</span><span class="chev" aria-hidden="true">▾</span></button>
        <button class="btn" id="repo-reset" ${stack ? "" : "hidden"} title="Put a file, or the whole repository, back the way it started">Reset</button>
        <span class="status" id="rt">${stack ? esc((envInfo(stack).test_command || "") ? "Tests: " + envInfo(stack).test_command : "") : ""}</span>
        <div class="spacer"></div>
        <span class="status save-st" id="save-st" aria-live="polite"></span>
        <button class="btn" id="run" ${stack ? "" : "disabled"}>Run tests</button>
        <button class="btn primary" id="submit" ${stack ? "" : "disabled"}>Submit</button>
      </div>
      <div class="ide" id="ide">${stack ? `<nav class="files" id="files" aria-label="Files"><div class="files-head">Explorer</div><div id="tree" class="tree"><p class="muted pad">Loading…</p></div></nav>
        <div class="ed-col"><div class="ftabs" id="ftabs" role="tablist" aria-label="Open files"></div><div class="editor" id="editor"></div></div>` : `<div class="env-pick" id="env-pick"><p class="muted pad">Loading environments…</p></div>`}</div>
      <div class="console${UI.min ? " min" : ""}" id="console" style="height:${UI.ch}px">
        <div class="rz-h" id="rz-h" role="separator" aria-orientation="horizontal" aria-label="Resize the test results panel" tabindex="0"></div>
        <div class="console-bar">
          <button class="ctoggle" id="ctoggle" aria-expanded="${!UI.min}" aria-controls="cbody"><span class="chev" aria-hidden="true">▾</span></button>
          <div class="ctabs" role="tablist"><button role="tab" data-ct="tests" aria-selected="${R.tab === "tests"}">Tests</button><button role="tab" data-ct="output" aria-selected="${R.tab === "output"}">Output</button></div>
          <span class="cstat" id="cstat"></span>
          <div class="spacer"></div>
          <span class="status keys">${MOD}+Enter run tests · ${MOD}+Shift+Enter submit · ${MOD}+S save</span>
        </div>
        <div class="console-body" id="cbody"><div id="out"><p class="muted">${stack ? "Run the tests to see which ones fail." : "Choose an environment to open the repository."}</p></div><pre class="out-log" id="out-log" hidden></pre></div>
      </div>
    </section>
  </div>`;
}

/* ---------- binding ---------- */
function bindRepo(e, q){
  const fit = () => { const ex = document.querySelector(".exam"), bar = document.querySelector(".bar"); if (ex && bar && innerWidth > 900) ex.style.height = (innerHeight - bar.getBoundingClientRect().bottom) + "px"; else if (ex) ex.style.height = ""; if (cm) cm.refresh(); };
  window.onresize = fit; setTimeout(fit, 0);
  bindPanels();
  bindNav(e);
  bindTimer(e);
  if (R.id !== q.id || R.stack !== e.lang[q.id] || R.ws !== repoWS()){ R.ws = repoWS(); R.id = q.id; R.stack = e.lang[q.id]; R.docs = {}; R.open = []; R.cur = null; R.tree = null; R.dirty.clear(); }
  document.querySelectorAll(".doc-tabs [data-doc]").forEach(b => b.addEventListener("click", () => showDoc(b.dataset.doc)));
  document.querySelectorAll(".ctabs [data-ct]").forEach(b => b.addEventListener("click", () => showConsoleTab(b.dataset.ct)));
  $("#run").addEventListener("click", () => repoRun(false));
  $("#submit").addEventListener("click", () => repoRun(true));
  $("#env-btn").addEventListener("click", ev => { ev.stopPropagation(); toggleEnvMenu(); });
  $("#repo-reset").addEventListener("click", () => resetDialog());
  showConsoleTab(R.tab);
  loadEnvs().then(() => {
    let stack = e.lang[q.id];
    if (!stack && e.practice){            // practice: if exactly one environment for this question is set up, open it
      const ready = repoStacks(q).filter(envReady);
      if (ready.length === 1){ e.lang[q.id] = stack = ready[0]; saveExam(); R.id = null; return render(); }
    }
    if (!stack || !envReady(stack)) return showPicker(e, q);
    $("#env-name").textContent = envInfo(stack).short || stack;
    openRepo(e, q);
  }).catch(err => { $("#ide").innerHTML = `<div class="env-pick"><div class="verdict bad">Couldn't reach the app</div><p class="muted">${esc(err.message)}</p></div>`; });
}
const envReady = k => R.envs && R.envs.envs[k] && R.envs.envs[k].state === "ready";
function loadEnvs(){ return rapi("/api/envs").then(s => (R.envs = s)); }

/* ---------- choosing an environment ---------- */
function showPicker(e, q){
  const ide = $("#ide");
  const cur = e.lang[q.id];
  const avail = repoStacks(q);
  const cards = ENV_ORDER.map(k => {
    const has = avail.includes(k), info = envInfo(k), st = has && R.envs.envs[k] ? R.envs.envs[k].state : "na";
    const chip = !has ? `<span class="chip na">Coming soon for this question</span>`
      : st === "ready" ? `<span class="chip ok">Ready</span>`
      : st === "blocked" ? `<span class="chip bad">Can't set up here</span>`
      : st === "outdated" ? `<span class="chip warn">Update needed</span>`
      : `<span class="chip">Needs setup · ${info.download_mb} MB download</span>`;
    const meta = !has ? "" : st === "ready" ? `${esc(Object.entries(info.installed || {}).filter(([n]) => n !== "Python").map(([n, v]) => n + " " + v).join(" · "))}`
      : st === "blocked" ? esc(info.plan.why) : `About ${info.disk_mb} MB on disk · ${esc(info.minutes || "")}`;
    return `<button class="env-card${cur === k ? " cur" : ""}" data-env="${k}" ${has ? "" : "disabled"}>
      <span class="env-top"><b>${esc(info.name)}</b>${chip}</span>
      <span class="env-sum">${esc(has ? info.summary || "" : info.lang + ". This repository isn't available in this stack yet.")}</span>
      ${meta ? `<span class="env-meta">${meta}</span>` : ""}</button>`;
  }).join("");
  ide.innerHTML = `<div class="env-pick" id="env-pick"><div class="env-inner">
    <h3>Choose your environment</h3>
    <p class="muted">The real OA asks you to pick a stack before it opens the repository. ${e.practice ? "In practice you can switch later; each environment keeps its own copy of your changes." : "<b>In a test you can't switch after you choose.</b>"}</p>
    <div class="env-cards">${cards}</div>
    <p class="muted small">Environments install into a private folder of this app, not system-wide. Set one up once and every repository question in that stack uses it.</p>
  </div></div>`;
  ide.querySelectorAll(".env-card:not([disabled])").forEach(b => b.addEventListener("click", () => chooseEnv(e, q, b.dataset.env)));
  const first = ide.querySelector(".env-card.cur, .env-card:not([disabled])"); if (first) first.focus();
}
function chooseEnv(e, q, k){
  if (lockedEnv(e, q.id) && e.lang[q.id] !== k) return toast("You chose " + envName(e.lang[q.id]) + " for this test. Switch environments in practice.");
  const go = () => {
    e.lang[q.id] = k;
    if (!e.practice){ e.envLock = e.envLock || {}; e.envLock[q.id] = true; }
    store.set("oa-repo-env", k); saveExam(); R.id = null; render();
  };
  if (envReady(k)) return go();
  setupDialog(k, go);
}

/* ---------- the setup dialog: what it installs, the size and the time, then live progress ---------- */
function envDialog(){
  let d = $("#env-dlg");
  if (!d){ d = document.createElement("dialog"); d.id = "env-dlg"; d.className = "oi-dlg"; d.setAttribute("aria-labelledby", "env-t"); document.body.appendChild(d);
    d.addEventListener("cancel", () => { clearInterval(R.poll); }); }
  return d;
}
function setupDialog(k, onReady){
  const d = envDialog(), info = envInfo(k), job = R.envs.job || {};
  const show = (html, focus) => { d.innerHTML = `<div class="oi-box">${html}</div>`; if (!d.open) d.showModal(); d.querySelectorAll("[data-close]").forEach(b => b.onclick = () => { clearInterval(R.poll); d.close(); }); const f = focus && d.querySelector(focus); if (f) f.focus(); };
  if (job.state === "running" && job.key && job.key !== k) return show(`<h3 id="env-t">One setup at a time</h3><p>${esc(envName(job.key))} is still being set up. Try ${esc(info.name)} when it finishes.</p><div class="oi-row"><button class="btn primary" data-close>OK</button></div>`, "[data-close]");
  if (job.state === "running") return progress(k, onReady, show);
  if (info.state === "blocked"){
    return show(`<h3 id="env-t">${esc(info.name)} can't be set up yet</h3><p>${esc(info.plan.why)}</p><p class="oi-note">${esc(info.plan.how || "")}</p>
      <div class="oi-row"><button class="btn" data-close>Close</button><button class="btn primary" id="env-again">Check again</button></div>`, "#env-again"),
      $("#env-again").onclick = () => loadEnvs().then(() => { if (envInfo(k).state !== "blocked") setupDialog(k, onReady); else toast("Still not found. Install it, then check again."); });
  }
  show(`<h3 id="env-t">Set up ${esc(info.name)}</h3>
    <p>${esc(info.summary)}.${info.state === "outdated" ? " The pinned versions changed since you set it up, so it's set up again." : ""}</p>
    <dl class="env-facts">
      <div><dt>Download</dt><dd>about ${info.download_mb} MB</dd></div>
      <div><dt>On disk</dt><dd>about ${info.disk_mb} MB</dd></div>
      <div><dt>Time</dt><dd>${esc(info.minutes)}</dd></div>
      <div><dt>Uses</dt><dd>${esc((info.plan && info.plan.uses) || info.needs || "")}</dd></div>
    </dl>
    <p class="oi-muted">It goes into the app's own folder (<code>.oa-cache/envs/${k}</code>); nothing else on your computer changes. You can remove it any time from the environment menu.</p>
    <div class="oi-row"><button class="btn" data-close>Not now</button><button class="btn primary" id="env-go">Set up ${esc(info.short || info.name)}</button></div>`, "#env-go");
  $("#env-go").onclick = () => rapi("/api/envs", {action: "install", key: k}).then(j => { R.envs.job = j; progress(k, onReady, show); })
    .catch(err => show(`<h3 id="env-t">Couldn't start</h3><p>${esc(err.message)}</p><div class="oi-row"><button class="btn primary" data-close>Close</button></div>`, "[data-close]"));
}
function progress(k, onReady, show){
  const info = envInfo(k);
  const draw = j => {
    const el = $("#env-log");
    if (el){ const atEnd = el.scrollTop + el.clientHeight >= el.scrollHeight - 8; el.textContent = j.log || ""; if (atEnd) el.scrollTop = el.scrollHeight; }
    const t = $("#env-time"); if (t) t.textContent = fmtTime(Date.now() - (j.started || Date.now() / 1000) * 1000);
  };
  show(`<h3 id="env-t"><span class="oi-spin" aria-hidden="true"></span>Setting up ${esc(info.name)}…</h3>
    <p class="oi-muted">Downloading about ${info.download_mb} MB. <span id="env-time"></span></p>
    <details class="oi-log" open><summary>Details</summary><pre id="env-log"></pre></details>
    <div class="oi-row"><button class="btn danger" id="env-stop">Stop</button></div>`, null);
  $("#env-stop").onclick = () => rapi("/api/envs", {action: "cancel"}).catch(() => {});
  clearInterval(R.poll);
  R.poll = setInterval(() => rapi("/api/envs").then(s => {
    R.envs = s; const j = s.job || {}; draw(j);
    if (j.state === "running") return;
    clearInterval(R.poll);
    if (j.state === "done"){
      const v = s.envs[k] && s.envs[k].installed ? Object.entries(s.envs[k].installed).map(([n, x]) => n + " " + x).join(" · ") : "";
      show(`<h3 id="env-t" class="oi-ok">${esc(info.name)} is ready</h3><p class="oi-muted">${esc(v)}${s.envs[k].size_mb ? " · " + s.envs[k].size_mb + " MB" : ""}</p>
        <div class="oi-row"><button class="btn primary" id="env-open">Open the repository</button></div>`, "#env-open");
      $("#env-open").onclick = () => { envDialog().close(); onReady(); };
    } else {
      show(`<h3 id="env-t">Setup didn't finish</h3><p>${esc(j.error || "Something went wrong.")}</p>
        <details class="oi-log" open><summary>Details</summary><pre>${esc(j.log || "")}</pre></details>
        <div class="oi-row"><button class="btn" data-close>Close</button><button class="btn primary" id="env-retry">Try again</button></div>`, "#env-retry");
      $("#env-retry").onclick = () => setupDialog(k, onReady);
    }
  }).catch(() => {}), 900);
}

/* ---------- the environment menu: switch, set up another, remove ---------- */
function toggleEnvMenu(){
  const old = $("#env-menu"); if (old){ old.remove(); $("#env-btn").setAttribute("aria-expanded", "false"); return; }
  const e = S.exam, q = QMAP[e.ids[e.cur]], cur = e.lang[q.id], locked = lockedEnv(e, q.id);
  const rows = ENV_ORDER.filter(k => R.envs.envs[k] || repoStacks(q).includes(k)).map(k => {
    const has = repoStacks(q).includes(k), info = envInfo(k), st = (R.envs.envs[k] || {}).state;
    const right = k === cur ? `<span class="chip ok">In use</span>` : !has ? `<span class="chip na">Not for this question</span>`
      : locked ? `<span class="chip na">Locked in this test</span>` : `<button class="btn sm" data-use="${k}">${st === "ready" ? "Switch" : "Set up"}</button>`;
    const rm = st === "ready" && k !== cur ? `<button class="linkbtn rm" data-rm="${k}">Remove${info.size_mb ? " · frees " + info.size_mb + " MB" : ""}</button>` : "";
    return `<div class="env-row"><div><b>${esc(info.name)}</b><div class="muted small">${st === "ready" ? "Set up" + (info.size_mb ? " · " + info.size_mb + " MB" : "") : st === "blocked" ? "Can't set up here" : has ? "Not set up · about " + info.download_mb + " MB" : "Not set up"} ${rm}</div></div>${right}</div>`;
  }).join("");
  const m = document.createElement("div");
  m.id = "env-menu"; m.className = "env-menu"; m.setAttribute("role", "dialog"); m.setAttribute("aria-label", "Environments");
  m.innerHTML = `<div class="env-menu-head">Environment</div>${rows}<div class="muted small env-foot">${locked ? "In a test the environment stays the one you chose." : "Each environment keeps its own copy of your changes."}</div>`;
  $("#env-btn").after(m); $("#env-btn").setAttribute("aria-expanded", "true");
  m.addEventListener("click", ev => ev.stopPropagation());
  m.querySelectorAll("[data-use]").forEach(b => b.onclick = () => { m.remove(); repoFlush().then(() => chooseEnv(e, q, b.dataset.use)); });
  m.querySelectorAll("[data-rm]").forEach(b => b.onclick = () => {
    if (!confirm("Remove " + envName(b.dataset.rm) + "? You can set it up again later. Your changes to repositories are kept.")) return;
    rapi("/api/envs", {action: "remove", key: b.dataset.rm}).then(s => { R.envs = s; m.remove(); toast(envName(b.dataset.rm) + " removed"); }).catch(err => toast(err.message));
  });
  setTimeout(() => document.addEventListener("click", function off(){ const x = $("#env-menu"); if (x) x.remove(); const b = $("#env-btn"); if (b) b.setAttribute("aria-expanded", "false"); document.removeEventListener("click", off); }), 0);
}

/* ---------- files ---------- */
function openRepo(e, q){
  const stack = e.lang[q.id];
  rapi(repoURL(q.id, stack, "tree")).then(t => {
    R.tree = t;
    drawTree();
    if (!cm){ cm = createEditor($("#editor"), "", "py"); cm.on("change", (c, ch) => { if (ch.origin !== "setValue") markDirty(); }); }
    const want = R.open.length ? R.open.slice() : (t.open || []).concat([]);
    R.open = [];
    const first = R.cur || want[want.length - 1];
    Promise.all(want.map(p => openFile(p, false))).then(() => { if (first) openFile(first, true); });
    loadReadme(stack);
    if (R.doc && R.doc !== "q") showDoc(R.doc);
    if (t.stale) toast("This repository was updated since you started. Reset it to get the new version.");
    const last = R.last[q.id + ":" + stack + ":" + repoWS()]; if (last) drawResults(last, true);
    const ed = $("#editor"); if (ed) ed.classList.toggle("ro", false);
  }).catch(err => { $("#ide").innerHTML = `<div class="env-pick"><div class="verdict bad">Couldn't open the repository</div><p class="muted">${esc(err.message)}</p></div>`; });
}
const modeOf = p => /\.py$/.test(p) ? ["python", "py"] : /\.(js|mjs|cjs|ts)$/.test(p) ? ["javascript", "js"] : /\.json$/.test(p) ? [{name: "javascript", json: true}, "js"]
  : /\.java$/.test(p) ? ["text/x-java", "java"] : [null, "py"];
function treeNodes(files){
  const root = {dirs: {}, files: []};
  files.forEach(f => { const parts = f.path.split("/"); let n = root; parts.slice(0, -1).forEach(p => { n = n.dirs[p] = n.dirs[p] || {dirs: {}, files: []}; }); n.files.push(f); });
  return root;
}
function drawTree(){
  const lock = `<svg class="ico" viewBox="0 0 16 16" aria-label="read-only"><rect x="3.5" y="7" width="9" height="6.5" rx="1.2" fill="none" stroke="currentColor" stroke-width="1.3"/><path d="M5.5 7V5a2.5 2.5 0 0 1 5 0v2" fill="none" stroke="currentColor" stroke-width="1.3"/></svg>`;
  const openDirs = new Set(R.open.concat(R.tree.open || []).flatMap(p => p.split("/").slice(0, -1).map((_, i, a) => a.slice(0, i + 1).join("/"))));
  const walk = (n, prefix, depth) => Object.keys(n.dirs).sort().map(d => {
    const path = prefix + d;
    return `<details class="dir" ${openDirs.has(path) || depth === 0 && Object.keys(n.dirs).length === 1 ? "open" : ""}><summary style="--d:${depth}"><span class="tw" aria-hidden="true">›</span>${esc(d)}</summary>${walk(n.dirs[d], path + "/", depth + 1)}</details>`;
  }).join("") + n.files.sort((a, b) => a.path.localeCompare(b.path)).map(f => {
    const name = f.path.split("/").pop();
    return `<button class="file${f.path === R.cur ? " cur" : ""}${f.changed ? " changed" : ""}" data-path="${esc(f.path)}" style="--d:${depth}" title="${esc(f.path)}${f.readonly ? " (read-only)" : ""}">
      <span class="fname">${esc(name)}</span>${f.readonly ? lock : ""}${f.changed ? `<span class="mod" title="changed">M</span>` : ""}</button>`;
  }).join("");
  $("#tree").innerHTML = walk(treeNodes(R.tree.files), "", 0);
  $("#tree").querySelectorAll(".file").forEach(b => b.addEventListener("click", () => openFile(b.dataset.path, true)));
}
function fileMeta(p){ return (R.tree.files || []).find(f => f.path === p) || {}; }
function openFile(path, focus){
  const have = R.docs[path];
  const ready = have ? Promise.resolve(have) : rapi(repoURL(R.id, R.stack, "file", {path})).then(f => {
    const [mode] = modeOf(path);
    const doc = CodeMirror.Doc(f.text, mode);
    R.docs[path] = {doc, readonly: f.readonly, saved: f.text};
    return R.docs[path];
  });
  return ready.then(d => {
    if (!R.open.includes(path)) R.open.push(path);
    if (focus){
      R.cur = path;
      cm.swapDoc(d.doc);
      cm.setOption("readOnly", d.readonly);
      cm.setOption("oaLang", modeOf(path)[1]);
      $("#editor").classList.toggle("ro", !!d.readonly);
      drawTabs(); drawTree();
      setTimeout(() => { cm.refresh(); cm.focus(); }, 0);
    } else drawTabs();
  }).catch(err => toast(err.message));
}
function drawTabs(){
  $("#ftabs").innerHTML = R.open.map(p => `<span class="ftab${p === R.cur ? " cur" : ""}" role="tab" aria-selected="${p === R.cur}">
    <button class="ft-open" data-path="${esc(p)}" title="${esc(p)}">${esc(p.split("/").pop())}${R.dirty.has(p) ? '<span class="dot" title="saving"></span>' : ""}${(R.docs[p] || {}).readonly ? '<span class="ro-tag">read-only</span>' : ""}</button>
    <button class="ft-x" data-close="${esc(p)}" aria-label="Close ${esc(p)}">×</button></span>`).join("");
  $("#ftabs").querySelectorAll(".ft-open").forEach(b => b.onclick = () => openFile(b.dataset.path, true));
  $("#ftabs").querySelectorAll(".ft-x").forEach(b => b.onclick = ev => { ev.stopPropagation(); closeFile(b.dataset.close); });
}
function closeFile(p){
  saveFile(p);
  const i = R.open.indexOf(p); if (i < 0) return;
  R.open.splice(i, 1);
  if (R.cur === p){ R.cur = null; const next = R.open[Math.min(i, R.open.length - 1)]; if (next) return openFile(next, true); cm.swapDoc(CodeMirror.Doc("", null)); cm.setOption("readOnly", "nocursor"); }
  drawTabs(); drawTree();
}
function markDirty(){
  const p = R.cur; if (!p || (R.docs[p] || {}).readonly) return;
  if (!R.dirty.has(p)){ R.dirty.add(p); drawTabs(); }
  setSave("Unsaved");
  clearTimeout(R.timers[p]); R.timers[p] = setTimeout(() => saveFile(p), 600);
}
function saveFile(p){
  const d = R.docs[p]; if (!d || !R.dirty.has(p)) return Promise.resolve();
  clearTimeout(R.timers[p]);
  const text = d.doc.getValue();
  R.dirty.delete(p);
  setSave("Saving…");
  return rapi(repoURL(R.id, R.stack, "file"), {path: p, text}).then(() => {
    d.saved = text;
    const f = fileMeta(p); const was = f.changed; f.changed = true;
    if (!was) drawTree();
    drawTabs(); setSave(R.dirty.size ? "Saving…" : "Saved");
  }).catch(err => { R.dirty.add(p); setSave("Not saved"); toast("Couldn't save " + p + ": " + err.message); });
}
function setSave(t){ const s = $("#save-st"); if (s) s.textContent = t; }
function repoFlush(){ return Promise.all([...R.dirty].map(saveFile)); }

/* ---------- README ---------- */
function loadReadme(stack){
  const b = document.querySelector('[data-doc="readme"]'); if (b) b.disabled = false;
  rapi(repoURL(R.id, stack, "file", {path: "README.md"})).then(f => { $("#doc-readme").innerHTML = mdHTML(f.text); })
    .catch(() => { $("#doc-readme").innerHTML = `<p class="muted">This repository has no README.md.</p>`; });
}
function showDoc(which){
  document.querySelectorAll(".doc-tabs [data-doc]").forEach(b => b.setAttribute("aria-selected", String(b.dataset.doc === which)));
  $("#doc-q").hidden = which !== "q"; $("#doc-readme").hidden = which !== "readme"; $("#doc-ai").hidden = which !== "ai";
  R.doc = which;
  if (which === "ai") drawAssist();
}
// Enough Markdown for a README: headings, paragraphs, lists, tables, code blocks, inline code, bold, italic, links.
function mdHTML(src){
  const inline = s => esc(s).replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>").replace(/(^|[^*])\*([^*\s][^*]*)\*/g, "$1<i>$2</i>")
    .replace(/\[([^\]]+)\]\((https?:[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  const lines = src.replace(/\r/g, "").split("\n"); let out = "", i = 0;
  while (i < lines.length){
    const l = lines[i];
    if (/^```/.test(l)){ let j = i + 1, code = []; while (j < lines.length && !/^```/.test(lines[j])) code.push(lines[j++]); out += `<pre>${esc(code.join("\n"))}</pre>`; i = j + 1; continue; }
    const h = l.match(/^(#{1,4})\s+(.*)/); if (h){ const n = Math.min(4, h[1].length + 1); out += `<h${n}>${inline(h[2])}</h${n}>`; i++; continue; }
    if (/^\|/.test(l) && i + 1 < lines.length && /^\|[\s:|-]+\|?\s*$/.test(lines[i + 1])){
      const row = r => r.replace(/^\||\|\s*$/g, "").split("|").map(c => c.trim());
      const head = row(l); let j = i + 2, body = [];
      while (j < lines.length && /^\|/.test(lines[j])) body.push(row(lines[j++]));
      out += `<div class="scroll-x"><table class="dtable"><thead><tr>${head.map(c => `<th>${inline(c)}</th>`).join("")}</tr></thead><tbody>${body.map(r => `<tr>${r.map(c => `<td>${inline(c)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
      i = j; continue;
    }
    if (/^\s*([-*]|\d+\.)\s+/.test(l)){
      const ordered = /^\s*\d+\./.test(l); let j = i, items = [];
      while (j < lines.length && /^\s*([-*]|\d+\.)\s+/.test(lines[j])){ let t = lines[j].replace(/^\s*([-*]|\d+\.)\s+/, ""); j++; while (j < lines.length && /^\s{2,}\S/.test(lines[j]) && !/^\s*([-*]|\d+\.)\s+/.test(lines[j])) t += " " + lines[j++].trim(); items.push(t); }
      out += `<${ordered ? "ol" : "ul"}>${items.map(t => `<li>${inline(t)}</li>`).join("")}</${ordered ? "ol" : "ul"}>`; i = j; continue;
    }
    if (!l.trim()){ i++; continue; }
    let j = i, para = [];
    while (j < lines.length && lines[j].trim() && !/^(#{1,4}\s|```|\||\s*([-*]|\d+\.)\s+)/.test(lines[j])) para.push(lines[j++]);
    out += `<p>${inline(para.join(" "))}</p>`; i = j;
  }
  return out;
}

/* ---------- reset ---------- */
function resetDialog(){
  const d = envDialog(), p = R.cur, ro = p && (R.docs[p] || {}).readonly;
  d.innerHTML = `<div class="oi-box"><h3 id="env-t">Reset</h3><p>Put your changes back the way the repository started.</p>
    <div class="oi-row"><button class="btn" data-close>Cancel</button>${p && !ro ? `<button class="btn" id="rs-file">Reset ${esc(p.split("/").pop())}</button>` : ""}<button class="btn danger" id="rs-all">Reset the whole repository</button></div></div>`;
  d.showModal();
  d.querySelector("[data-close]").onclick = () => d.close();
  const done = t => { R.tree = t; Object.keys(R.docs).forEach(k => delete R.docs[k]); R.dirty.clear(); const open = R.open.slice(), cur = R.cur; R.open = [];
    Promise.all(open.map(x => openFile(x, false))).then(() => { if (cur) openFile(cur, true); }); drawTree(); d.close(); setSave(""); toast("Reset"); };
  const f = $("#rs-file"); if (f) f.onclick = () => { R.dirty.delete(p); rapi(repoURL(R.id, R.stack, "reset"), {path: p}).then(done).catch(err => toast(err.message)); };
  $("#rs-all").onclick = () => { R.dirty.clear(); rapi(repoURL(R.id, R.stack, "reset"), {}).then(done).catch(err => toast(err.message)); };
}

/* ---------- Run tests / Submit ---------- */
function showConsoleTab(t){
  R.tab = t;
  document.querySelectorAll(".ctabs [data-ct]").forEach(b => b.setAttribute("aria-selected", String(b.dataset.ct === t)));
  const o = $("#out"), l = $("#out-log"); if (o) o.hidden = t !== "tests"; if (l) l.hidden = t !== "output";
}
async function repoRun(full){
  const e = S.exam; if (!e || e.ended || R.busy) return;
  const id = e.ids[e.cur], q = QMAP[id], stack = e.lang[id];
  if (!stack || !envReady(stack)) return toast("Choose an environment first");
  R.busy = true; $("#run").disabled = $("#submit").disabled = true;
  if (UI.min) setConsole(false);
  setStat(full ? "Submitting…" : "Running tests…", "");
  showConsoleTab("tests");
  $("#out").innerHTML = `<div class="running-line"><span class="oi-spin" aria-hidden="true"></span>${full ? "Running every test, including the hidden ones" : "Running " + esc(envInfo(stack).test_command || "the tests")}…</div>`;
  try {
    await repoFlush();
    const res = await rapi(repoURL(id, stack, "run"), {scope: full ? "all" : "visible", reveal: !!e.practice});
    res.full = full;
    R.last[id + ":" + stack + ":" + repoWS()] = res;
    if (full){
      const b = e.best[id];
      if (!b || res.score >= b.score) e.best[id] = {score: res.score, passed: res.passed, total: res.total, lang: stack, at: Date.now()};
      saveExam();
      const tab = document.querySelector(`.qtab[data-q="${e.cur}"] .dot`); if (tab) tab.className = "dot " + (e.best[id].score === 100 ? "full" : e.best[id].score > 0 ? "part" : "");
    }
    drawResults(res);
    assistAfterRun();
  } catch (err){
    $("#out").innerHTML = `<div class="verdict bad">Couldn't run the tests</div><p>${esc(err.message)}</p>`; setStat("Error", "bad");
  } finally { R.busy = false; const r = $("#run"), s = $("#submit"); if (r) r.disabled = false; if (s) s.disabled = false; }
}
function drawResults(res, quiet){
  const e = S.exam, id = e.ids[e.cur], b = e.best[id];
  const failed = res.total - res.passed;
  const head = res.full
    ? `<div class="verdict ${failed ? "bad" : "ok"}">${failed ? `${res.passed} of ${res.total} tests passed` : `All ${res.total} tests passed`}<span class="status">Score ${res.score}/100${b ? " · best " + b.score + "/100" : ""} · ${(res.ms / 1000).toFixed(1)} s</span></div>`
    : `<div class="verdict ${failed ? "bad" : "ok"}">${failed ? `${failed} of ${res.total} test${res.total === 1 ? "" : "s"} failed` : `All ${res.total} tests pass`}<span class="status">${(res.ms / 1000).toFixed(1)} s</span></div>`;
  const icon = ok => ok ? `<span class="ic ok" aria-label="passed">✓</span>` : `<span class="ic bad" aria-label="failed">✗</span>`;
  let first = !quiet;
  const rows = res.tests.map(t => t.ok || t.hidden
    ? `<li class="rtest ${t.ok ? "ok" : "bad"}">${icon(t.ok)}<span class="t">${esc(t.title)}</span>${t.name ? `<code>${esc(t.name)}</code>` : ""}</li>`
    : `<li class="rtest bad"><details ${first && !(first = false) ? "open" : ""}><summary>${icon(false)}<span class="t">${esc(t.title)}</span><code>${esc(t.name)}</code></summary>
        <pre class="msg">${esc(t.message || "")}</pre>${t.detail ? `<details class="tb"><summary>Full traceback</summary><pre>${esc(t.detail)}</pre></details>` : ""}</details></li>`).join("");
  const hiddenNote = !res.full && R.tree && R.tree.hidden ? `<p class="muted small">${R.tree.hidden} more tests run when you submit.</p>` : "";
  $("#out").innerHTML = head + (res.timed_out ? `<p class="warn-line">The tests took too long and were stopped. An endless loop or a request that never answers?</p>` : "")
    + `<ul class="rtests">${rows}</ul>` + hiddenNote;
  $("#out-log").textContent = res.output || "(no output)";
  setStat(res.full ? `${res.score}/100` : `${res.passed}/${res.total} passed`, failed ? "bad" : "ok");
}

/* ---------- glue for the rest of the app ---------- */
// Practice reopens the environment you used last when this question has it; a test always asks first.
function repoDefault(q, practice){
  const pref = store.get("oa-repo-env", null);
  return practice && pref && repoStacks(q).includes(pref) ? pref : null;
}
function saveNow(){
  const q = S.exam && QMAP[S.exam.ids[S.exam.cur]];
  if (q && q.type === "repo") repoFlush().then(() => setSave("Saved")); else { saveCode(); toast("Saved"); }
}
// In the report: what was broken and the fix, fetched when you open it.
function repoReview(q, stack){
  if (!stack) return `<div class="status">No environment was chosen.</div>`;
  return `<details class="sol" data-repo-sol="${esc(q.id)}" data-stack="${esc(stack)}"><summary>What was broken, and the fix (${esc(envName(stack))})</summary><div class="sol-body"><p class="muted">Loading…</p></div></details>`;
}
document.addEventListener("toggle", ev => {
  const d = ev.target;
  if (!(d instanceof HTMLDetailsElement) || !d.open || !d.dataset.repoSol || d.dataset.loaded) return;
  d.dataset.loaded = "1";
  rapi(repoURL(d.dataset.repoSol, d.dataset.stack, "solution")).then(s => {
    d.querySelector(".sol-body").innerHTML = `<ol class="bugs">${s.bugs.map(b => `<li><b>${esc(b.file)}</b>: ${esc(b.why)}.${b.fix ? `<div class="muted">${esc(b.fix)}</div>` : ""}</li>`).join("")}</ol>`
      + Object.entries(s.files).map(([p, t]) => `<details class="sol"><summary>Fixed ${esc(p)}</summary><pre>${esc(t)}</pre></details>`).join("");
  }).catch(err => { d.querySelector(".sol-body").innerHTML = `<p class="muted">${esc(err.message)}</p>`; });
}, true);
