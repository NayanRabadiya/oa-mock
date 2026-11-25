#!/usr/bin/env node
// Runs SQL queries and JavaScript programs the way the test page does, for the question checks
// (app/server/contribute.py). It loads the page's own code, so a check can't pass here and fail in the browser:
//   SQL:        app/web/static/js/run/sql.js (sqlRun, sameRows) with the bundled AlaSQL
//   JavaScript: the Web Worker source in app/web/static/js/run/workers.js (JS_WORKER)
//
// Reads one JSON request on stdin and prints one JSON answer:
//   {"mode": "sql", "query": "...", "tests": [{"tables": {...}, "out": [[...]]}]}
//       -> [{"ok": bool, "rows": [[...]], "cols": [...]} | {"ok": false, "err": "..."}]
//   {"mode": "js", "src": "...", "inputs": ["..."], "limit": 4000}
//       -> [{"out": "...", "err": "...", "ms": n, "tle": bool}]
"use strict";
const fs = require("fs"), path = require("path"), vm = require("vm"), os = require("os");
const { Worker, isMainThread, parentPort, workerData } = require("worker_threads");
const WEB = path.join(__dirname, "..", "app", "web", "static");
const read = (...p) => fs.readFileSync(path.join(WEB, ...p), "utf8");

function sqlEngine() {
  const alasql = require(path.join(WEB, "vendor", "alasql", "alasql.min.js"));
  const ctx = vm.createContext({ alasql });
  return vm.runInContext(read("js", "run", "sql.js") + "\n;({sqlRun, sameRows})", ctx);
}

function workerSource() {
  const stub = { Worker: function () {}, URL: { createObjectURL: () => "" }, Blob: function () {} };
  return vm.runInContext(read("js", "run", "workers.js") + "\n;JS_WORKER", vm.createContext(stub));
}

// Each run gets its own thread, like the page's fresh Web Worker: globals the program changes (Date.now, ...)
// don't leak, and a program stuck in a loop is stopped by terminating the thread.
function runJs(worker, src, inp, limit) {
  return new Promise((resolve) => {
    const t = new Worker(__filename, { workerData: { worker, src, inp } });
    let done = false;
    const finish = (r) => { if (!done) { done = true; clearTimeout(timer); t.terminate(); resolve(r); } };
    const timer = setTimeout(() => finish({ out: "", err: "", ms: limit, tle: true }), limit);
    t.on("message", (m) => finish({ out: m.out, err: m.err, ms: m.ms, tle: false }));
    t.on("error", (e) => finish({ out: "", err: String(e && e.message || e), ms: 0, tle: false }));
    t.on("exit", () => finish({ out: "", err: "the program exited without finishing", ms: 0, tle: false }));
  });
}

function inThread({ worker, src, inp }) {
  const ctx = vm.createContext({
    postMessage: (m) => parentPort.postMessage(m),
    performance, setTimeout, clearTimeout, setInterval, clearInterval, queueMicrotask,
    TextEncoder, TextDecoder, URL, structuredClone,
  });
  vm.runInContext(worker, ctx);
  ctx.onmessage({ data: { id: 1, src, inp } });
}

async function main() {
  const req = JSON.parse(fs.readFileSync(0, "utf8"));
  let out;
  if (req.mode === "sql") {
    const { sqlRun, sameRows } = sqlEngine();
    out = req.tests.map((t) => {
      try {
        const got = sqlRun(req.query, t);
        const rows = JSON.parse(JSON.stringify(got.rows));     // undefined -> null, so it survives JSON
        return { ok: sameRows(got.rows, t.out || []), rows, cols: got.cols };
      } catch (e) {
        return { ok: false, err: String(e && e.message || e) };
      }
    });
  } else if (req.mode === "js") {
    const worker = workerSource();
    out = new Array(req.inputs.length);
    let next = 0;
    const lane = async () => { while (next < req.inputs.length) { const i = next++; out[i] = await runJs(worker, req.src, req.inputs[i], req.limit || 4000); } };
    await Promise.all(Array.from({ length: Math.min(4, os.cpus().length || 1) }, lane));    // a few tests at a time
  } else {
    throw new Error("mode must be sql or js");
  }
  process.stdout.write(JSON.stringify(out));
  process.exit(0);     // don't wait for timers a hung program left behind
}

if (!isMainThread) inThread(workerData);
else main().catch((e) => { process.stderr.write(String(e && e.stack || e)); process.exit(2); });
