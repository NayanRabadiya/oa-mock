"use strict";
// Small helpers shared by every module.

/* ---------- helpers ---------- */
const esc = s => String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const $ = s => document.querySelector(s);
const norm = s => String(s).replace(/\r/g,"").split("\n").map(l => l.replace(/\s+$/,"")).join("\n").replace(/\n+$/,"").replace(/^\n+/,"");
const fmtTime = ms => { ms = Math.max(0, ms); const s = Math.floor(ms/1000), h = Math.floor(s/3600), m = Math.floor(s%3600/60), x = s%60; return (h ? h+":" : "") + String(m).padStart(2,"0") + ":" + String(x).padStart(2,"0"); };
const pick = a => a[Math.floor(Math.random()*a.length)];
const byDiff = d => QS.filter(q => q.diff === d);
const ORDER = {Easy:0, Medium:1, Hard:2, SQL:3, Debug:4, SJT:5};
const bankIds = () => [...QS].sort((a, b) => ORDER[a.diff] - ORDER[b.diff]).map(q => q.id);
const touched = (e, id) => !!(e.best[id] || (e.ans && e.ans[id] && Object.keys(e.ans[id]).length) || Object.entries(e.code[id] || {}).some(([l, c]) => c !== starterOf(QMAP[id], l)));
const starterOf = (q, lang) => (q && q.stub && q.stub[lang] != null) ? q.stub[lang] : (q && q.starter != null) ? q.starter : STARTER[lang];
const srcOf = (q, code, lang) => q.type === "debug" ? q.pre + "\n" + code + "\n" + q.post : (q.driver && q.driver[lang]) ? q.driver[lang].pre + code + q.driver[lang].post : code;
const cmpOut = (q, out) => norm(q.type === "debug" ? String(out).split("\n").filter(l => !l.startsWith("[log]")).join("\n") : out);
const sjtMax = q => q.items.length * 2;
const sjtScore = (q, ans) => { const a = ans || {}; let p = 0; q.items.forEach((it, i) => { if (a[i] != null) p += it.o[a[i]][1]; }); return p; };
const sjtAnswered = (q, ans) => Object.keys(ans || {}).length;
