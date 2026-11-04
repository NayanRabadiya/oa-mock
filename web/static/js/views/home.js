"use strict";
// Home page: formats, question bank, resume banner, past attempts.

function homeHTML(){
  const best = store.get(K + "-best", {}), hist = store.get(K + "-history", []);
  const fm = Object.entries(FORMATS).map(([k, f]) => `<label class="fmt"><input type="radio" name="fmt" id="fmt-${k}" value="${k}" ${S.fmt === k ? "checked" : ""}><b>${f.name}</b><span>${f.desc}</span></label>`).join("");
  const custom = S.fmt === "custom" ? `<div class="custom-pick">${QS.map(q => `<label><input type="checkbox" id="cp-${q.id}" value="${q.id}" ${S.custom.includes(q.id) ? "checked" : ""}> ${esc(q.title)} <span class="pill d-${q.diff}">${q.diff}</span></label>`).join("")}</div>` : "";
  const bank = bankIds().map(id => QMAP[id]).map(q => `<div class="bank-row"><span class="pill d-${q.diff}">${q.diff}</span><div><div class="t">${esc(q.title)}</div><div class="s">${esc(q.src)}</div></div><div>${best[q.id] != null ? `<span class="best">best ${best[q.id]}/100</span>` : ""}<button class="btn" data-practice="${q.id}">Practise</button></div></div>`).join("")
    + OFFLIST.map(o => `<div class="bank-row off"><span class="pill">Not runnable</span><div><div class="t">${esc(o.t)}</div><div class="s">${esc(o.s)} · ${esc(o.why)}</div></div><div>${o.link ? `<a class="btn" href="${o.link}" target="_blank" rel="noopener">Open</a>` : ""}</div></div>`).join("");
  const hrows = hist.map(h => `<tr><td>${new Date(h.at).toLocaleString([], {day:"numeric", month:"short", hour:"2-digit", minute:"2-digit"})}</td><td>${esc(FORMATS[h.fmt] ? FORMATS[h.fmt].name : h.fmt)}</td><td>${h.per.map(p => esc(QMAP[p.id] ? QMAP[p.id].title : p.id) + " " + p.s).join(" · ")}</td><td class="n">${h.score}/${h.max}</td><td class="n">${fmtTime(h.used)}${h.untimed ? ` <span class="muted">untimed</span>` : ""}</td></tr>`).join("");
  return `
  <header class="bar"><div class="brand">${esc(CFG.name)}<small>${LOCAL ? "Local runner · C++ ready" : "Practice test room"}</small></div>${LOCAL ? `<div class="spacer"></div><a class="btn" href="/">All companies</a>` : ""}</header>
  <main class="wrap">
    ${S.exam && !S.exam.ended ? resumeHTML() : ""}
    <section class="hero"><h1>${esc(CFG.headline)}</h1>
      <p>${QS.length} ${esc(CFG.blurb)}, each with its own hidden tests. No camera, no microphone, no proctoring. ${LOCAL ? "You are on the local runner: C++17, Java and Python compile and run on your own computer." : "Python and JavaScript run in your browser, and the SQL question runs against an in-browser database. For C++ or Java, open the test through the local runner file."}</p></section>
    <section class="panel" aria-labelledby="h-start"><h2 id="h-start">Start a test</h2>
      <div class="formats">${fm}</div>${custom}
      <div class="setup-row">
        <label class="field" for="mins">Minutes<input id="mins" type="number" min="5" max="240" value="${S.fmt === "custom" ? S.customMins : FORMATS[S.fmt].mins}" style="width:90px" ${S.untimed ? "disabled" : ""}></label>
        <label class="field chk" for="untimed">Timer<span class="box"><input type="checkbox" id="untimed" ${S.untimed ? "checked" : ""}> No timer</span></label>
        <label class="field" for="lang0">Language<select id="lang0">${CODE_LANGS.map(l => `<option value="${l}" ${S.lang === l ? "selected" : ""}>${LANGS[l].label}</option>`).join("")}</select></label>
        <button class="btn primary" id="go">Start test</button>
      </div>
      <ul class="rules"><li>Run checks the sample cases. Submit runs all hidden tests and keeps your best score for each question.</li><li>Partial marks: score = tests passed / total × 100, like HackerRank.</li><li>The test ends when the timer runs out. Tick <b>No timer</b> to work without a limit: the clock counts up instead and you end the test yourself. Leaving the tab is counted and shown in the report.</li><li>${esc(CFG.ioRule || "Read input from STDIN and print to STDOUT. Do not print extra text.")}</li></ul>
    </section>
    <section class="panel" aria-labelledby="h-bank"><h2 id="h-bank">Question bank</h2><div class="bank">${bank}</div></section>
    ${homeSubsHTML()}
    ${hist.length ? `<section class="panel" aria-labelledby="h-hist"><h2 id="h-hist">Past attempts</h2><div class="scroll-x"><table class="hist"><thead><tr><th>When</th><th>Format</th><th>Questions</th><th>Score</th><th>Time</th></tr></thead><tbody>${hrows}</tbody></table></div></section>` : ""}
  </main>`;
}
function resumeHTML(){
  const e = S.exam, q = QMAP[e.ids[e.cur]];
  const name = e.practice ? "Practice session" : (FORMATS[e.fmt] ? FORMATS[e.fmt].name : "Test") + " in progress";
  const done = e.ids.filter(id => e.best[id]).length;
  return `<section class="panel resume" aria-live="polite"><div class="grow"><b>${esc(name)}</b><div class="status">${e.practice ? `On ${esc(q.title)}` : `Q${e.cur + 1} of ${e.ids.length} · ${done} submitted · <span id="rs-time">${resumeTime(e)}</span>`}</div></div>
    <button class="btn primary" id="rs-go">Resume</button><button class="btn" id="rs-end">${e.practice ? "Finish practice" : "End test"}</button></section>`;
}
function resumeTime(e){
  if (e.untimed) return fmtTime(Date.now() - e.start) + " elapsed, no limit";
  const left = e.start + e.dur - Date.now();
  return left > 0 ? fmtTime(left) + " left (the timer keeps running)" : "time is up";
}
function guardStart(go){
  const e = S.exam;
  if (!e || e.ended || e.practice) return go();
  const m = $("#modal");
  m.innerHTML = `<div class="box" role="dialog" aria-modal="true" aria-labelledby="m-t"><h3 id="m-t" style="font-size:20px">Discard the test in progress?</h3><p class="muted" style="margin:0">Starting something new ends your current ${esc(FORMATS[e.fmt] ? FORMATS[e.fmt].name : "")} test without saving it to Past attempts. To keep it, resume it and end it first.</p><div class="row"><button class="btn" id="m-no">Keep it</button><button class="btn primary" id="m-yes">Discard and start</button></div></div>`;
  m.hidden = false; $("#m-no").focus();
  $("#m-no").onclick = closeModal; $("#m-yes").onclick = () => { closeModal(); go(); };
}
function bindHome(){
  fillHomeSubs();
  if (S.exam && !S.exam.ended){
    $("#rs-go").addEventListener("click", () => { S.view = "exam"; render(); });
    $("#rs-end").addEventListener("click", () => S.exam.practice ? endExam(false) : confirmEnd());
    if (!S.exam.practice) tick = setInterval(() => { const t = $("#rs-time"); if (t) t.textContent = resumeTime(S.exam); }, 1000);
  }
  document.querySelectorAll('input[name="fmt"]').forEach(r => r.addEventListener("change", () => { S.fmt = r.value; render(); }));
  document.querySelectorAll(".custom-pick input").forEach(c => c.addEventListener("change", () => { S.custom = [...document.querySelectorAll(".custom-pick input:checked")].map(x => x.value); }));
  $("#lang0").addEventListener("change", e => { S.lang = e.target.value; store.set(K + "-lang", S.lang); });
  $("#mins").addEventListener("change", e => { if (S.fmt === "custom") S.customMins = +e.target.value || 60; });
  $("#untimed").addEventListener("change", e => { S.untimed = e.target.checked; store.set(K + "-untimed", S.untimed); $("#mins").disabled = S.untimed; });
  $("#go").addEventListener("click", () => {
    const ids = buildSet(S.fmt);
    if (!ids.length) { $("#go").textContent = "Pick at least one question"; return; }
    guardStart(() => startExam(S.fmt, ids, Math.max(5, +$("#mins").value || 90), false, S.untimed));
  });
  document.querySelectorAll("[data-practice]").forEach(b => b.addEventListener("click", () => guardStart(() => {
    const ids = bankIds(), e = S.exam;
    if (e && !e.ended && e.practice && e.ids.join() === ids.join()){ saveExam(); e.cur = ids.indexOf(b.dataset.practice); saveExam(); S.view = "exam"; render(); return; }
    startExam("practice", ids, 0, true, false, ids.indexOf(b.dataset.practice));
  })));
}
