
// ---- file: app.js + test client (read-only) -----------------------------
return (async () => {
  const realNow = Date.now;
  let clock = 1767225600000;            // 2026-01-01T00:00:00Z
  Date.now = () => clock;
  const router = (typeof watchlistRouter !== "undefined") ? watchlistRouter : null;
  if (!router) { __out.push("watchlistRouter is not defined"); return; }
  const matchPath = (pat, path) => {
    const a = pat.replace(/\/+$/, "").split("/"), b = path.replace(/\/+$/, "").split("/");
    if (a.length !== b.length) return null;
    const params = {};
    for (let i = 0; i < a.length; i++) {
      if (a[i].startsWith(":")) params[a[i].slice(1)] = decodeURIComponent(b[i]);
      else if (a[i] !== b[i]) return null;
    }
    return params;
  };
  const show = body => {
    if (Array.isArray(body)) return JSON.stringify(body.map(x => x && typeof x === "object" && typeof x.title === "string" ? x.title : x));
    return JSON.stringify(body === undefined ? null : body);
  };
  async function request(method, url, user, body) {
    const sub = url.replace(/^\/api\/watchlist/, "") || "/";
    const req = { method, path: sub, originalUrl: url, params: {}, body: body || {}, headers: user === "-" ? {} : { authorization: "Bearer token-" + user } };
    let sent = null;
    const res = {
      statusCode: 200,
      status(c) { this.statusCode = c; return this; },
      json(b) { if (sent) { __log("Error [ERR_HTTP_HEADERS_SENT]: Cannot set headers after they are sent to the client"); return this; } sent = { code: this.statusCode, body: b }; return this; },
      send(b) { return this.json(b); }
    };
    const layers = router.stack.filter(l => l.all || (l.method === method && matchPath(l.path, sub)));
    const chain = [];
    for (const l of layers) { if (!l.all) req.params = matchPath(l.path, sub); for (const h of l.h) chain.push(h); }
    const routed = layers.some(l => !l.all);
    const run = async i => {
      if (sent) return;
      if (i >= chain.length) { if (!routed) res.status(404).json({ message: "Cannot " + method + " " + url }); return; }
      let p;
      try { p = chain[i](req, res, () => run(i + 1)); if (p && typeof p.then === "function") await p; }
      catch (e) { __log(e); if (!sent) res.status(500).json({ message: "Internal Server Error" }); }
    };
    await run(0);
    for (let k = 0; k < 5 && !sent; k++) await new Promise(r => setTimeout(r, 0));
    return sent || { code: 504, body: { message: "No response: the request never finished (it would time out)" } };
  }
  try {
  const lines = require("fs").readFileSync().split("\n").map(l => l.trim()).filter(l => l && !l.startsWith("#"));
  for (const line of lines) {
    const m = line.match(/^(\d+)\s+(\S+)\s+(GET|POST)\s+(\S+)\s*(.*)$/);
    if (!m) { __out.push("bad test line: " + line); continue; }
    clock = 1767225600000 + Number(m[1]) * 1000;
    let body = {};
    if (m[5]) body = JSON.parse(m[5]);
    const r = await request(m[3], m[4], m[2], body);
    __out.push(r.code + " " + show(r.body));
  }
  } finally { Date.now = realNow; }
  process.stdout.write(__out.join("\n") + "\n");
})();
