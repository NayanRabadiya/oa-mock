"""Repository questions: a real project you debug in the app, like HackerRank's Code Repository questions.

data/<company>/repos/<qid>/<stack>/
  repo/          what you get: the project, with the bugs, its README and the visible tests
  solution/      the fixed versions of the files that have bugs (shown after the test; used by the checks)
  hidden/        more test files, added only when you submit
  repo.json      read-only files, files open at the start, the tests with readable titles, the bugs

Your working copy lives in .oa-cache/repos/<company>/<qid>/<stack>/ (git-ignored): edits are saved there and
the tests run there. Submit runs a scratch copy with the read-only files put back and the hidden tests added.

  tree(...)         files, which are read-only, which you changed
  read / write      one file
  reset(...)        one file, or the whole repo, back to the start
  run(..., "visible" | "all")   runs the tests; per-test results and the output
"""
import fnmatch, hashlib, json, os, shutil, signal, subprocess, sys, tempfile, threading, time
import xml.etree.ElementTree as ET

from . import data, envs, submissions

WORK_DIR = os.path.join(submissions.CACHE_DIR, "repos")
IS_WIN = os.name == "nt"
MAX_FILE = 512 * 1024
SKIP_DIRS = {"__pycache__", "node_modules", ".git", "target", ".pytest_cache", ".gradle", "build"}
SKIP_FILES = {"db.sqlite3", ".DS_Store"}
TEST_TIMEOUT = 180
OUTPUT_MAX = 60000
_locks = {}
_locks_lock = threading.Lock()


class RepoError(ValueError):
    pass


def _lock(key):
    with _locks_lock:
        return _locks.setdefault(key, threading.Lock())


def src_dir(company, qid, stack):
    if not (data.KEY_RE.match(company or "") and data.KEY_RE.match(qid or "") and data.KEY_RE.match(stack or "")):
        raise RepoError("bad name")
    d = os.path.join(data.DATA_DIR, company, "repos", qid, stack)
    if not os.path.isfile(os.path.join(d, "repo.json")):
        raise RepoError("this question has no %s repository" % stack)
    return d


def manifest(company, qid, stack):
    with open(os.path.join(src_dir(company, qid, stack), "repo.json"), encoding="utf-8") as f:
        return json.load(f)


def stacks_of(company, qid):
    d = os.path.join(data.DATA_DIR, company, "repos", qid)
    return sorted(s for s in os.listdir(d) if os.path.isfile(os.path.join(d, s, "repo.json"))) if os.path.isdir(d) else []


def _files(root):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".oa"))
        for f in sorted(filenames):
            if f in SKIP_FILES or f.startswith(".oa") or f.endswith((".pyc", ".class")):
                continue
            out.append(os.path.relpath(os.path.join(dirpath, f), root).replace(os.sep, "/"))
    return out


def _digest(root):
    h = hashlib.sha256()
    for rel in _files(root):
        h.update(rel.encode()); h.update(b"\0")
        with open(os.path.join(root, rel), "rb") as f:
            h.update(f.read())
    return h.hexdigest()[:16]


WS_RE = __import__("re").compile(r"^[a-z0-9][a-z0-9-]{0,39}$")
KEEP_TESTS = 5          # timed-test copies kept per question, besides practice


def work_dir(company, qid, stack, ws="practice", create=True):
    """Your copy of the repo. Practice has one copy per stack; every timed test starts from a fresh copy of its own."""
    src = src_dir(company, qid, stack)
    if not WS_RE.match(ws or ""):
        raise RepoError("bad workspace")
    d = os.path.join(WORK_DIR, company, qid, stack, ws)
    if create and not os.path.isfile(os.path.join(d, ".oa-base.json")):
        with _lock(d):
            if not os.path.isfile(os.path.join(d, ".oa-base.json")):
                shutil.rmtree(d, ignore_errors=True)
                shutil.copytree(os.path.join(src, "repo"), d, ignore=shutil.ignore_patterns(*SKIP_DIRS))
                with open(os.path.join(d, ".oa-base.json"), "w", encoding="utf-8") as f:
                    json.dump({"base": _digest(os.path.join(src, "repo")), "at": time.time()}, f)
                if ws != "practice":
                    _prune(os.path.dirname(d))
    return d


def _prune(stack_dir):
    tests = sorted((os.path.getmtime(os.path.join(stack_dir, w)), w) for w in os.listdir(stack_dir) if w != "practice")
    for _, w in tests[:-KEEP_TESTS]:
        shutil.rmtree(os.path.join(stack_dir, w), ignore_errors=True)


def _readonly(m, rel):
    return any(fnmatch.fnmatchcase(rel, pat) for pat in m.get("readonly", []))


def _safe(root, rel):
    rel = (rel or "").replace("\\", "/").strip("/")
    if not rel or rel.startswith("../") or "/../" in "/" + rel + "/" or rel.split("/")[0].startswith(".oa"):
        raise RepoError("bad path")
    p = os.path.normpath(os.path.join(root, rel))
    if not (p + os.sep).startswith(os.path.normpath(root) + os.sep):
        raise RepoError("bad path")
    return rel, p


def tree(company, qid, stack, ws="practice"):
    m = manifest(company, qid, stack)
    start = os.path.join(src_dir(company, qid, stack), "repo")
    d = work_dir(company, qid, stack, ws)
    out = []
    for rel in _files(d):
        orig = os.path.join(start, rel)
        changed = not os.path.isfile(orig) or not _same(orig, os.path.join(d, rel))
        out.append({"path": rel, "readonly": _readonly(m, rel), "changed": changed})
    with open(os.path.join(d, ".oa-base.json"), encoding="utf-8") as f:
        base = json.load(f).get("base")
    return {"files": out, "open": m.get("open", []), "name": m.get("name"), "stack": stack,
            "tests": [{"id": t["id"], "title": t["title"]} for t in m["tests"] if not t.get("hidden")],
            "hidden": sum(1 for t in m["tests"] if t.get("hidden")),
            "stale": base != _digest(start)}


def _same(a, b):
    try:
        with open(a, "rb") as x, open(b, "rb") as y:
            return x.read() == y.read()
    except OSError:
        return False


def read(company, qid, stack, rel, ws="practice"):
    d = work_dir(company, qid, stack, ws)
    rel, p = _safe(d, rel)
    if not os.path.isfile(p):
        raise RepoError("no such file")
    if os.path.getsize(p) > MAX_FILE:
        raise RepoError("this file is too large to open here")
    with open(p, "rb") as f:
        raw = f.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise RepoError("not a text file")
    return {"path": rel, "text": text, "readonly": _readonly(manifest(company, qid, stack), rel)}


def write(company, qid, stack, rel, text, ws="practice"):
    m = manifest(company, qid, stack)
    d = work_dir(company, qid, stack, ws)
    rel, p = _safe(d, rel)
    if _readonly(m, rel):
        raise RepoError("%s is read-only" % rel)
    if not isinstance(text, str) or len(text.encode("utf-8")) > MAX_FILE:
        raise RepoError("file too large")
    if not os.path.isfile(p):
        raise RepoError("no such file")
    with _lock(d):
        tmp = p + ".oa-tmp"
        with open(tmp, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        os.replace(tmp, p)
    return {"path": rel, "saved": time.time()}


def reset(company, qid, stack, rel=None, ws="practice"):
    start = os.path.join(src_dir(company, qid, stack), "repo")
    d = work_dir(company, qid, stack, ws)
    with _lock(d):
        if rel:
            rel, p = _safe(d, rel)
            orig = os.path.join(start, rel)
            if not os.path.isfile(orig):
                raise RepoError("no such file in the original repository")
            shutil.copyfile(orig, p)
        else:
            shutil.rmtree(d, ignore_errors=True)
    if not rel:
        work_dir(company, qid, stack, ws)
    return tree(company, qid, stack, ws)


def changed_files(company, qid, stack, ws="practice"):
    """{path: text} of the files you changed (for the submission record)."""
    start = os.path.join(src_dir(company, qid, stack), "repo")
    d = work_dir(company, qid, stack, ws)
    out = {}
    for rel in _files(d):
        orig = os.path.join(start, rel)
        if not os.path.isfile(orig) or not _same(orig, os.path.join(d, rel)):
            try:
                with open(os.path.join(d, rel), encoding="utf-8") as f:
                    out[rel] = f.read()
            except (OSError, UnicodeDecodeError):
                pass
    return out


# ------------------------------------------------------------------ running the tests

def _kill(p):
    try:
        if IS_WIN:
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            os.killpg(p.pid, signal.SIGKILL)
    except Exception:
        try: p.kill()
        except Exception: pass


def _command(stack, project, report):
    if stack == "django":
        return [envs.python("django"), os.path.join(envs.ENV_SRC, "django", "run_tests.py"), project, report]
    raise RepoError("%s isn't supported yet" % stack)


def _run_in(stack, project, timeout=TEST_TIMEOUT):
    """Runs the stack's tests in `project`. Returns ({test id: {status, message, time}}, output, timed_out)."""
    report = os.path.join(tempfile.mkdtemp(prefix="oa-report-"), "unit.xml")
    extra = {"creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0)} if IS_WIN else {"start_new_session": True}
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUNBUFFERED="1")
    p = subprocess.Popen(_command(stack, project, report), cwd=project, stdin=subprocess.DEVNULL,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, **extra)
    timed_out = False
    try:
        out, _ = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        _kill(p)
        out, _ = p.communicate()
    output = out.decode("utf-8", "replace").replace(project + os.sep, "").replace(project, ".")
    results = {}
    try:
        root = ET.parse(report).getroot()
        for case in root.iter("testcase"):
            tid = "%s.%s" % (case.get("classname"), case.get("name"))
            status, msg = "passed", ""
            for child in case:
                if child.tag in ("failure", "error", "skipped"):
                    status = {"failure": "failed", "error": "error", "skipped": "skipped"}[child.tag]
                    msg = (child.text or child.get("message") or "").replace(project + os.sep, "").replace(project, ".")
            results[tid] = {"status": status, "message": msg, "time": float(case.get("time") or 0)}
    except (OSError, ET.ParseError):
        pass
    finally:
        shutil.rmtree(os.path.dirname(report), ignore_errors=True)
    if len(output) > OUTPUT_MAX:
        output = output[:OUTPUT_MAX // 2] + "\n… %d characters cut …\n" % (len(output) - OUTPUT_MAX) + output[-OUTPUT_MAX // 2:]
    return results, output, timed_out


def _short_message(msg):
    """The useful end of a traceback: the assertion and the line of the test that made it."""
    lines = [l for l in (msg or "").strip().splitlines() if l.strip()]
    if not lines:
        return ""
    tail = lines[-1]
    where = next((l.strip() for l in reversed(lines[:-1]) if l.strip().startswith("File ")), "")
    return (tail + ("\n" + where if where else ""))[:800]


def _graded(m, results, output, timed_out, scope, reveal_hidden):
    rows = []
    hidden_n = 0
    for t in m["tests"]:
        if t.get("hidden") and scope != "all":
            continue
        r = results.get(t["id"])
        status = r["status"] if r else ("timeout" if timed_out else "error")
        row = {"id": t["id"], "hidden": bool(t.get("hidden")), "status": status, "ok": status == "passed",
               "time": round(r["time"], 3) if r else None}
        if t.get("hidden"):
            hidden_n += 1
            row["title"] = t["title"] if reveal_hidden else "Hidden test %d" % hidden_n
            row["name"] = t["id"].rsplit(".", 1)[-1] if reveal_hidden else ""
        else:
            row["title"] = t["title"]
            row["name"] = t["id"].rsplit(".", 1)[-1]
            if not row["ok"]:
                row["message"] = _short_message(r["message"]) if r else (
                    "The tests didn't finish in %d s." % TEST_TIMEOUT if timed_out else "This test didn't run: see the output.")
                row["detail"] = (r or {}).get("message", "")[-4000:]
        rows.append(row)
    passed = sum(r["ok"] for r in rows)
    return {"tests": rows, "passed": passed, "total": len(rows), "score": round(100 * passed / len(rows)) if rows else 0,
            "output": output, "timed_out": timed_out}


def run(company, qid, stack, scope="visible", reveal_hidden=False, ws="practice"):
    """Runs the visible tests in your working copy, or (scope "all", Submit) every test in a scratch copy with the
    read-only files restored and the hidden tests added."""
    if not envs.ready(stack):
        raise RepoError("set up the %s environment first" % stack)
    m = manifest(company, qid, stack)
    src = src_dir(company, qid, stack)
    d = work_dir(company, qid, stack, ws)
    t0 = time.time()
    with _lock(d + ":run"):
        if scope != "all":
            results, output, to = _run_in(stack, d)
        else:
            with tempfile.TemporaryDirectory(prefix="oa-submit-") as tmp:
                proj = os.path.join(tmp, "repo")
                shutil.copytree(d, proj, ignore=shutil.ignore_patterns(*SKIP_DIRS, ".oa*", *SKIP_FILES))
                _overlay_readonly(m, os.path.join(src, "repo"), proj)
                if os.path.isdir(os.path.join(src, "hidden")):
                    shutil.copytree(os.path.join(src, "hidden"), proj, dirs_exist_ok=True)
                results, output, to = _run_in(stack, proj)
    res = _graded(m, results, output, to, scope, reveal_hidden)
    res["ms"] = round((time.time() - t0) * 1000)
    if scope == "all":
        res["output"] = _hide_hidden_names(m, res["output"]) if not reveal_hidden else res["output"]
    return res


def _overlay_readonly(m, start, proj):
    for rel in _files(start):
        if _readonly(m, rel):
            os.makedirs(os.path.dirname(os.path.join(proj, rel)) or proj, exist_ok=True)
            shutil.copyfile(os.path.join(start, rel), os.path.join(proj, rel))


def _hide_hidden_names(m, output):
    """During a test the hidden tests stay hidden: their names are replaced and their failure tracebacks (which
    quote the test's code) are left out of the output."""
    n = 0
    for t in m["tests"]:
        if t.get("hidden"):
            n += 1
            cls, _, name = t["id"].rpartition(".")
            output = output.replace(name, "hidden_test_%d" % n).replace(cls, "hidden")
    keep, skipping = [], False
    for line in output.splitlines():
        if line.startswith(("FAIL: hidden_test_", "ERROR: hidden_test_")):
            skipping = True
            keep.append(line + "   (details hidden during the test)")
            continue
        if skipping and (line.startswith("=" * 20) or line.startswith("Ran ")):
            skipping = False
        if not skipping:
            keep.append(line)
    return "\n".join(keep)


def solution(company, qid, stack):
    """{path: fixed text} for the files that had bugs, plus the bug list (for the report after the test)."""
    m = manifest(company, qid, stack)
    sol = os.path.join(src_dir(company, qid, stack), "solution")
    files = {}
    for rel in _files(sol) if os.path.isdir(sol) else []:
        with open(os.path.join(sol, rel), encoding="utf-8") as f:
            files[rel] = f.read()
    return {"files": files, "bugs": [{k: b.get(k) for k in ("file", "why", "fix")} for b in m.get("bugs", [])]}


# ------------------------------------------------------------------ checks (tools/add_question.py and the PR check)

def _project_with(src, files):
    """A scratch copy of the starting repo, with `files` ({path: text}) written over it and the hidden tests added."""
    tmp = tempfile.mkdtemp(prefix="oa-check-")
    proj = os.path.join(tmp, "repo")
    shutil.copytree(os.path.join(src, "repo"), proj, ignore=shutil.ignore_patterns(*SKIP_DIRS))
    if os.path.isdir(os.path.join(src, "hidden")):
        shutil.copytree(os.path.join(src, "hidden"), proj, dirs_exist_ok=True)
    for rel, text in files.items():
        with open(os.path.join(proj, rel), "w", encoding="utf-8", newline="") as f:
            f.write(text)
    return tmp, proj


def verify(company, qid, stack):
    """[(check name, status, detail)] for one stack of a repository question."""
    out = []
    try:
        m = manifest(company, qid, stack)
        src = src_dir(company, qid, stack)
    except (RepoError, ValueError, OSError) as e:
        return [("%s repository" % stack, "fail", str(e))]
    label = m.get("name") or stack
    ids = [t["id"] for t in m.get("tests", [])]
    errs = []
    if not ids or len(set(ids)) != len(ids):
        errs.append('"tests" must list each test id once')
    if not any(not t.get("hidden") for t in m.get("tests", [])):
        errs.append("there must be at least one visible test")
    start_files = set(_files(os.path.join(src, "repo")))
    for rel in _files(os.path.join(src, "solution")) if os.path.isdir(os.path.join(src, "solution")) else []:
        if rel not in start_files:
            errs.append("solution/%s isn't a file of the repository" % rel)
    for b in m.get("bugs", []):
        if not (isinstance(b, dict) and b.get("file") in start_files and b.get("why") and b.get("edits")):
            errs.append('each bug needs "file" (a file of the repo), "why" and "edits"'); break
    if errs:
        return [("%s: format" % stack, "fail", "\n".join(errs))]
    if not envs.ready(stack):
        return [("%s: tests" % stack, "skip", "set up the %s environment to run these (the pull-request check runs them)" % stack)]
    solved = {}
    for rel in _files(os.path.join(src, "solution")):
        with open(os.path.join(src, "solution", rel), encoding="utf-8") as f:
            solved[rel] = f.read()
    def run_with(files):
        tmp, proj = _project_with(src, files)
        try:
            results, output, to = _run_in(stack, proj)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        failed = [t for t in ids if (results.get(t) or {}).get("status") != "passed"]
        return failed, output, to
    short = lambda t: t.rsplit(".", 1)[-1]
    failed, output, to = run_with(solved)
    if failed:
        out.append(("%s: fixed repository passes" % stack, "fail", "%d/%d tests pass with the fixes in solution/. Failing: %s\n%s"
                    % (len(ids) - len(failed), len(ids), ", ".join(map(short, failed[:5])), output[-1500:])))
        return out
    out.append(("%s: fixed repository passes" % stack, "ok", "%d/%d tests pass with the fixes in solution/ (%s)" % (len(ids), len(ids), label)))
    failed, _, _ = run_with({})
    visible = [t["id"] for t in m["tests"] if not t.get("hidden")]
    vf = [t for t in failed if t in visible]
    out.append(("%s: starting repository fails" % stack, "ok" if vf else "fail",
                "the starting repository fails %d of %d visible tests and %d of %d in all" % (len(vf), len(visible), len(failed), len(ids))
                if vf else "the starting repository passes every visible test, so there's nothing to debug"))
    bugs = m.get("bugs", [])
    if not bugs:
        out.append(("%s: each bug is needed" % stack, "warn", 'no "bugs" listed'))
        return out
    notes, status = [], "ok"
    all_back = dict(solved)
    for b in bugs:
        text = solved.get(b["file"])
        if text is None:
            notes.append("can't apply: %s: %s has no fixed version in solution/" % (b["why"], b["file"])); status = "fail"; continue
        bad = None
        for e in b["edits"]:
            n = text.count(e["fixed"])
            if n != 1:
                bad = "%s in solution/%s: %r" % ("not found" if n == 0 else "found %d times" % n, b["file"], e["fixed"][:70]); break
            text = text.replace(e["fixed"], e["buggy"])
            all_back[b["file"]] = all_back[b["file"]].replace(e["fixed"], e["buggy"], 1)
        if bad:
            notes.append("can't apply: %s: %s" % (b["why"], bad)); status = "fail"; continue
        f, _, _ = run_with(dict(solved, **{b["file"]: text}))
        if f:
            want = b.get("test")
            extra = "" if not want or any(short(x) == want for x in f) else "  (expected it to fail %s)" % want
            notes.append("needed: %s (fails %s)%s" % (b["why"], ", ".join(map(short, f[:4])) + (" …" if len(f) > 4 else ""), extra))
            if extra:
                status = "warn" if status == "ok" else status
        else:
            notes.append("NOT needed: %s: with only this bug every test passes" % b["why"]); status = "fail"
    start = os.path.join(src, "repo")
    differs = [rel for rel, text in all_back.items() if not _same_text(os.path.join(start, rel), text)]
    if status != "fail":
        if differs:
            status = "warn"
            notes.insert(0, "putting every bug back doesn't give the starting files (%s): is a bug missing from the list?" % ", ".join(differs))
        else:
            notes.insert(0, "all %d bugs are caught one at a time, and putting them all back gives the starting files exactly" % len(bugs))
    out.append(("%s: each bug is needed" % stack, status, "\n".join(notes)))
    return out


def _same_text(path, text):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read() == text
    except OSError:
        return False
