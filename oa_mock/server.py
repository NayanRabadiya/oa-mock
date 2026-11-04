"""HTTP server: serves the web app and runs code. Listens on 127.0.0.1 only.

GET  /                               company picker
GET  /<company>                      the test app for one company
GET  /static/...                     CSS, JS and vendored libraries from web/static/
GET  /api/companies                  JSON list of companies
GET  /api/companies/<company>/data.js   window.OA_DATA = {config, questions}
POST /run                            {lang, code, inputs[], limit} -> {results[]} or {compile_error}
"""
import html, json, mimetypes, os, secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import data, judge

WEB_DIR = os.path.join(data.ROOT, "web")
STATIC_DIR = os.path.join(WEB_DIR, "static")
TOKEN = secrets.token_hex(16)   # /run only accepts requests from pages this server rendered
MAX_INPUTS = 50

mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("text/css", ".css")


def _template(name, **values):
    with open(os.path.join(WEB_DIR, name), encoding="utf-8") as f:
        text = f.read()
    for k, v in values.items():
        text = text.replace("{{%s}}" % k, v)
    return text


class Handler(BaseHTTPRequestHandler):
    server_version = "OAMock"

    def log_message(self, *args):
        pass

    # Only answer requests addressed to this server (blocks DNS-rebinding pages).
    def _host_ok(self):
        port = self.server.server_address[1]
        return self.headers.get("Host", "") in ("127.0.0.1:%d" % port, "localhost:%d" % port)

    def _send(self, code, body, ctype, cache="no-cache"):
        b = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", cache)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(b)

    def _not_found(self):
        self._send(404, "not found", "text/plain; charset=utf-8")

    def do_GET(self):
        if not self._host_ok():
            return self._send(403, "forbidden", "text/plain")
        path = self.path.split("?", 1)[0]
        parts = [p for p in path.split("/") if p]

        if not parts:
            links = "".join('<a class="company" href="/%s">%s<small>%s</small></a>' % (k, html.escape(n), html.escape(t))
                            for k, n, t in data.companies())
            return self._send(200, _template("index.html", companies=links), "text/html; charset=utf-8")

        if parts[0] == "static":
            return self._static(parts[1:])

        if parts[0] == "api":
            if parts[1:] == ["companies"]:
                body = json.dumps([{"key": k, "name": n, "tagline": t} for k, n, t in data.companies()])
                return self._send(200, body, "application/json")
            if len(parts) == 4 and parts[1] == "companies" and parts[3] == "data.js":
                js = data.as_script(parts[2])
                return self._send(200, js, "text/javascript; charset=utf-8") if js else self._not_found()
            return self._not_found()

        if parts == ["favicon.ico"]:
            return self._send(204, b"", "image/x-icon")

        if len(parts) == 1:
            p = data.load(parts[0])
            if p is None:
                return self._not_found()
            page = _template("app.html", title=html.escape(p["config"].get("name", parts[0])),
                             token=json.dumps(TOKEN), company=parts[0])
            return self._send(200, page, "text/html; charset=utf-8")
        self._not_found()

    def _static(self, parts):
        if not parts or any(p in ("..", ".") or p.startswith(".") for p in parts):
            return self._not_found()
        full = os.path.realpath(os.path.join(STATIC_DIR, *parts))
        if not full.startswith(os.path.realpath(STATIC_DIR) + os.sep) or not os.path.isfile(full):
            return self._not_found()
        ctype = mimetypes.guess_type(full)[0] or "application/octet-stream"
        if ctype.startswith("text/"):
            ctype += "; charset=utf-8"
        with open(full, "rb") as f:
            self._send(200, f.read(), ctype)

    def do_POST(self):
        if (self.path != "/run" or not self._host_ok() or self.headers.get("X-Token") != TOKEN
                or "application/json" not in self.headers.get("Content-Type", "")):
            return self._send(403, '{"error":"forbidden"}', "application/json")
        try:
            n = int(self.headers.get("Content-Length", "0"))
            req = json.loads(self.rfile.read(n) or b"{}")
            res = judge.judge(req.get("lang"), req.get("code", ""), list(req.get("inputs", []))[:MAX_INPUTS],
                              float(req.get("limit", 2000)))
        except Exception as e:
            res = {"compile_error": "Runner error: %s" % e}
        self._send(200, json.dumps(res), "application/json")


def serve(port, tries=20):
    """Bind to 127.0.0.1:port, or the next free port. Returns the server."""
    for p in range(port, port + tries):
        try:
            return ThreadingHTTPServer(("127.0.0.1", p), Handler)
        except OSError:
            if p == port:
                print("\nPort %d is busy. An older copy may still be running (Ctrl+Z only pauses it)." % p)
                print("Stop it with  kill %%1  or  lsof -ti tcp:%d | xargs kill . Trying the next port..." % p)
    raise SystemExit("No free port between %d and %d." % (port, port + tries - 1))
