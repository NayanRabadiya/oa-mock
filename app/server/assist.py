"""The assistant for repository questions: a hint ladder that needs nothing, and a chat with an AI model using the
learner's own API key.

Hints come from the question's own notes on each bug (repo.json): where to look, what's wrong, how to fix it. Only
the bugs behind the tests that fail right now are offered, one step at a time.

The chat reads the question, the README, the repository as it is in your working copy and the latest test results,
and answers. In "coach" mode it is told to guide you without writing the fix; "full" mode helps the way the
real OA's assistant does. Keys are kept on this computer only, in .oa-cache/assistant.json (git-ignored), and are
sent only to the provider they belong to; the page never sees them again after you save them.

  providers()                     the providers, their models and whether a key is saved
  configure({...})                save a provider's key / model / address, or which provider to use
  models(provider)                ask the provider which models it has
  hints(co, qid, stack, failing)  the hint ladder for the failing visible tests
  chat(co, qid, stack, ws, req)   one reply from the model
"""
import html, json, os, re, threading, urllib.error, urllib.request

from . import repos, submissions

CONFIG = os.path.join(submissions.CACHE_DIR, "assistant.json")
TIMEOUT = 120
CONTEXT_BUDGET = 90000        # characters of repository code sent with each question
MAX_TURNS = 24                # earlier messages beyond this are dropped
MAX_REPLY_TOKENS = 1500
_lock = threading.Lock()

PROVIDERS = {
    "anthropic": {"name": "Claude (Anthropic)", "kind": "anthropic", "url": "https://api.anthropic.com/v1/messages",
                  "models_url": "https://api.anthropic.com/v1/models", "model": "claude-sonnet-5-5",
                  "suggest": ["claude-sonnet-5-5", "claude-haiku-5-5", "claude-opus-5-5"],
                  "keys": "https://console.anthropic.com/settings/keys"},
    "openai": {"name": "OpenAI", "kind": "openai", "url": "https://api.openai.com/v1/chat/completions",
               "models_url": "https://api.openai.com/v1/models", "model": "gpt-5.6-sol",
               "suggest": ["gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna"], "max_param": "max_completion_tokens",
               "keys": "https://platform.openai.com/api-keys"},
    "gemini": {"name": "Google Gemini", "kind": "openai",
               "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
               "models_url": "https://generativelanguage.googleapis.com/v1beta/openai/models", "model": "gemini-flash-latest",
               "suggest": ["gemini-flash-latest", "gemini-pro-latest"], "keys": "https://aistudio.google.com/apikey"},
    "openrouter": {"name": "OpenRouter (DeepSeek, Qwen, Llama and more)", "kind": "openai",
                   "url": "https://openrouter.ai/api/v1/chat/completions", "models_url": "https://openrouter.ai/api/v1/models",
                   "model": "deepseek/deepseek-chat", "suggest": ["deepseek/deepseek-chat", "qwen/qwen3-coder"],
                   "keys": "https://openrouter.ai/keys"},
    "ollama": {"name": "Ollama (a model on this computer)", "kind": "openai", "nokey": True,
               "url": "http://127.0.0.1:11434/v1/chat/completions", "models_url": "http://127.0.0.1:11434/v1/models",
               "model": "qwen2.5-coder:7b", "suggest": ["qwen2.5-coder:7b", "llama3.1:8b"], "keys": "https://ollama.com/download"},
}


class AssistError(ValueError):
    pass


# ---------- settings ----------
def _load():
    try:
        with open(CONFIG, encoding="utf-8") as f:
            cfg = json.load(f)
        return cfg if isinstance(cfg, dict) else {}
    except (OSError, ValueError):
        return {}


def _save(cfg):
    os.makedirs(os.path.dirname(CONFIG), exist_ok=True)
    tmp = CONFIG + ".tmp"
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)   # readable by you only
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=1)
    os.replace(tmp, CONFIG)


def _settings(cfg, key):
    p = PROVIDERS[key]
    mine = (cfg.get("providers") or {}).get(key) or {}
    return {"key": mine.get("key", ""), "model": mine.get("model") or p["model"], "url": mine.get("url") or p["url"]}


def providers():
    cfg = _load()
    out = {}
    for k, p in PROVIDERS.items():
        s = _settings(cfg, k)
        out[k] = {"name": p["name"], "model": s["model"], "suggest": p["suggest"], "keys": p["keys"],
                  "nokey": bool(p.get("nokey")), "has_key": bool(s["key"]) or bool(p.get("nokey")),
                  "key_end": s["key"][-4:] if len(s["key"]) > 8 else "", "url": s["url"], "default_url": p["url"]}
    current = cfg.get("provider") if cfg.get("provider") in PROVIDERS else None
    return {"provider": current, "providers": out, "file": CONFIG}


def configure(req):
    key = req.get("provider")
    if key not in PROVIDERS:
        raise AssistError("unknown provider")
    with _lock:
        cfg = _load()
        mine = cfg.setdefault("providers", {}).setdefault(key, {})
        if "key" in req:
            k = str(req.get("key") or "").strip()
            if k:
                if len(k) > 400 or not re.fullmatch(r"[\x21-\x7e]+", k):
                    raise AssistError("That doesn't look like an API key")
                mine["key"] = k
            elif req.get("forget"):
                mine.pop("key", None)
        if "model" in req:
            m = str(req.get("model") or "").strip()
            if len(m) > 120:
                raise AssistError("model name too long")
            mine["model"] = m
        if "url" in req:
            u = str(req.get("url") or "").strip()
            if u and not re.match(r"^https?://", u):
                raise AssistError("the address must start with http:// or https://")
            mine["url"] = u
        if req.get("use", True):
            cfg["provider"] = key
        _save(cfg)
    return providers()


# ---------- calling a provider ----------
def _post(url, headers, body):
    data = json.dumps(body).encode("utf-8")
    r = urllib.request.Request(url, data=data, headers=dict(headers, **{"Content-Type": "application/json"}), method="POST")
    return _open(r)


def _open(r):
    try:
        with urllib.request.urlopen(r, timeout=TIMEOUT) as res:
            return json.loads(res.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")[:2000]
        try:
            j = json.loads(raw)
            err = j.get("error")
            msg = (err.get("message") if isinstance(err, dict) else err) or j.get("message") or raw
        except ValueError:
            msg = raw
        hint = {401: "The key was refused. Check it, or make a new one.", 403: "The key isn't allowed to use this model.",
                404: "The provider doesn't know this model or address.", 429: "Too many requests, or no credit left on this key."}.get(e.code, "")
        raise AssistError(("%s (HTTP %d: %s)" % (hint, e.code, str(msg)[:300])).strip())
    except urllib.error.URLError as e:
        raise AssistError("Couldn't reach the provider: %s" % (e.reason,))
    except (TimeoutError, OSError) as e:
        raise AssistError("The provider didn't answer in time (%s)" % e)
    except ValueError:
        raise AssistError("The provider sent something that isn't JSON")


def _headers(key, s):
    p = PROVIDERS[key]
    if p["kind"] == "anthropic":
        return {"x-api-key": s["key"], "anthropic-version": "2023-06-01"}
    h = {"Authorization": "Bearer " + s["key"]} if s["key"] else {}
    if key == "openrouter":
        h.update({"HTTP-Referer": "https://github.com/rgabhi/oa-mock", "X-Title": "OA Mock"})
    return h


def _need(key):
    if key not in PROVIDERS:
        raise AssistError("Choose a provider first")
    s = _settings(_load(), key)
    if not s["key"] and not PROVIDERS[key].get("nokey"):
        raise AssistError("Add an API key for %s first" % PROVIDERS[key]["name"])
    return s


def _complete(key, system, messages):
    p, s = PROVIDERS[key], _need(key)
    if p["kind"] == "anthropic":
        res = _post(s["url"], _headers(key, s), {"model": s["model"], "max_tokens": MAX_REPLY_TOKENS, "system": system,
                                                "messages": messages})
        text = "".join(b.get("text", "") for b in res.get("content") or [] if b.get("type") == "text")
    else:
        body = {"model": s["model"], "messages": [{"role": "system", "content": system}] + messages,
                p.get("max_param", "max_tokens"): MAX_REPLY_TOKENS}
        res = _post(s["url"], _headers(key, s), body)
        choice = (res.get("choices") or [{}])[0]
        content = (choice.get("message") or {}).get("content")
        text = content if isinstance(content, str) else "".join(c.get("text", "") for c in content or [] if isinstance(c, dict))
    if not text.strip():
        raise AssistError("The model sent an empty reply")
    return {"text": text.strip(), "model": s["model"], "provider": key}


def models(key):
    p = PROVIDERS.get(key)
    if not p:
        raise AssistError("unknown provider")
    s = _need(key)
    url = p["models_url"]
    if s["url"] != p["url"]:                    # your own address: ask the same server
        for tail in ("/chat/completions", "/messages"):
            if s["url"].endswith(tail):
                url = s["url"][: -len(tail)] + "/models"
    res = _open(urllib.request.Request(url + ("?limit=100" if p["kind"] == "anthropic" else ""), headers=_headers(key, s)))
    ids = sorted({str(m.get("id", "")).replace("models/", "") for m in res.get("data") or res.get("models") or [] if m.get("id")})
    return {"models": ids[:500]}


# ---------- what the model is told ----------
def _text(html_src):
    t = re.sub(r"<(br|/p|/li|/h\d|/div|/tr)\s*/?>", "\n", html_src or "", flags=re.I)
    t = re.sub(r"<li[^>]*>", "- ", t, flags=re.I)
    return html.unescape(re.sub(r"<[^>]+>", "", t)).strip()


def _question(company, qid):
    path = os.path.join(repos.data.ROOT, "data", company, "questions", qid + ".json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _repo_context(company, qid, stack, ws, current):
    """The working copy as the learner sees it: the open file first, then the README, then the rest, within budget."""
    t = repos.tree(company, qid, stack, ws)
    paths = [f["path"] for f in t["files"]]
    order = ([current] if current in paths else []) + [p for p in ("README.md",) if p != current and p in paths]
    order += [p for p in paths if p not in order and not p.endswith((".lock", "package-lock.json", ".png", ".jpg", ".ico"))]
    listing = "\n".join("%s%s%s" % (f["path"], "  (read-only)" if f["readonly"] else "", "  (changed)" if f["changed"] else "")
                        for f in t["files"])
    parts, used, left_out = [], 0, []
    for p in order:
        try:
            body = repos.read(company, qid, stack, p, ws).get("text", "")
        except (repos.RepoError, OSError):
            continue
        if used + len(body) > CONTEXT_BUDGET:
            left_out.append(p)
            continue
        used += len(body)
        parts.append("=== %s ===\n%s" % (p, body))
    if left_out:
        parts.append("(Not included to save space: %s)" % ", ".join(left_out))
    return listing, "\n\n".join(parts)


COACH = """You are the assistant in a practice online assessment: a repository question like HackerRank's Code Repository tasks. The learner must find and fix the bugs that make the tests fail.

Coach mode. Help them learn to debug, and do not solve it for them:
- Never write the corrected code, a diff or the exact changed line, even if they ask. Pseudocode of the fix counts as writing it.
- Point them toward the right test, file or function; explain what a failing assertion or error message means; ask a guiding question; explain the concepts (HTTP status codes, ORM queries, middleware, off-by-one bounds, async/await...).
- If they are stuck after a couple of hints, narrow it down more (which function, which condition), but still let them make the change.
- They may write a fix and ask you to check it: then say whether it is right and why.
Keep answers short and concrete. Use Markdown, and `backticks` for code names."""

FULL = """You are the AI assistant in an online assessment with an AI-assisted repository task, like Amazon's AI-assisted OA on HackerRank. The candidate must find and fix the bugs that make the tests fail.

Full help mode: answer like a capable pair programmer. You may explain the bugs and show corrected code. Prefer showing only the changed lines with the file name. Point out when a change could break another test or another rule in the README. Keep answers concise. Use Markdown, and `backticks` for code names."""


def chat(company, qid, stack, ws, req):
    key = req.get("provider") or _load().get("provider")
    if key not in PROVIDERS:
        raise AssistError("Choose a provider first")
    msgs = [m for m in (req.get("messages") or []) if isinstance(m, dict) and m.get("role") in ("user", "assistant")
            and isinstance(m.get("content"), str) and m["content"].strip()]
    if not msgs or msgs[-1]["role"] != "user":
        raise AssistError("Nothing to answer")
    msgs = msgs[-MAX_TURNS:]
    while msgs and msgs[0]["role"] != "user":
        msgs.pop(0)
    q = _question(company, qid)
    m = repos.manifest(company, qid, stack)
    listing, code = _repo_context(company, qid, stack, ws, str(req.get("file") or ""))
    run = str(req.get("results") or "No test run yet.")[:12000]
    system = (FULL if req.get("mode") == "full" else COACH) + "\n\n" + "\n\n".join([
        "## The question\n" + _text(q.get("body")),
        "## Environment\n%s. Tests run with the stack's usual command. Read-only files (the tests among them) can't be changed." % (m.get("name") or stack),
        "## Files\n" + listing,
        "## Latest test results\n" + run,
        "## The repository (the learner's current working copy; the first file is the one open in the editor)\n" + code])
    return _complete(key, system, [{"role": x["role"], "content": x["content"][:8000]} for x in msgs])


# ---------- hints ----------
def hints(company, qid, stack, failing):
    """The hint ladder for each failing visible test: where to look, what's wrong, how to fix it."""
    m = repos.manifest(company, qid, stack)
    visible = [t for t in m["tests"] if not t.get("hidden")]
    failing = set(failing or [])

    def matches(bug_test, test_id):
        tail = test_id.rsplit(".", 1)[-1]
        return bug_test in (test_id, tail) or test_id.endswith("." + bug_test) or tail == "test_" + bug_test

    out = []
    for t in visible:
        if t["id"] not in failing:
            continue
        bugs = [b for b in m.get("bugs", []) if matches(b.get("test", ""), t["id"])]
        steps = []
        for b in bugs:
            why = b.get("why", "").rstrip(".")
            steps.append([
                "Look in `%s`." % b["file"],
                (why[:1].upper() + why[1:] + ".") if why else "Compare what this file does with the rule in the README.",
                b.get("fix") or "Change the code so it follows the rule in the README.",
            ])
        out.append({"id": t["id"], "title": t["title"], "bugs": steps})
    return {"tests": out}
