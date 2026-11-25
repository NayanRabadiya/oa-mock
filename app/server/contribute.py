"""Adding a question: check it, save it into data/, and send it as a pull request.

check(company, q)   runs every check the pull-request check runs (tools/add_question.py is the same from a terminal):
                    format, the function spec (generates the LeetCode stub + hidden driver in 4 languages), the
                    reference solutions on every test, the 4 drivers reading every input the same way, known-wrong
                    solutions failing, and duplicates already in the bank. SQL questions: the reference query and the
                    known-wrong queries in AlaSQL; debugging: the fixed files pass, the starting files fail, each
                    listed bug is needed; SJT: the scenarios and their scores. SQL and debugging run the page's own
                    code under Node (tools/js_check.js).
save(company, q)    writes data/<company>/questions/<id>.json (and company.json for a new company), and refreshes the
                    local catalog.
share(company, qid) commits just those files on top of GitHub's main branch, without touching your working copy,
                    pushes them to your fork with the GitHub CLI (gh) and opens a pull request.
"""
import contextlib, io, json, os, re, subprocess, sys, tempfile, time

from . import data, judge, library

TOOLS = os.path.join(data.ROOT, "tools")
STYLE = os.path.join(TOOLS, "style")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,39}$")
DIFFS = ("Easy", "Medium", "Hard")
TYPES = ("code", "sql", "debug", "sjt", "repo")
LABEL = {"sql": "SQL", "debug": "Debug", "sjt": "SJT", "repo": "Repo"}          # their "diff" (the pill in the bank)
NAME = {"code": "coding", "sql": "SQL", "debug": "debugging", "sjt": "situational-judgement", "repo": "repository"}
JS_LIMIT = 4000                      # what JavaScript gets in the page (LIMIT.js)
PY_LIMIT = 5000                      # what a Python answer gets on the platform (grading.LIMIT_MS)
MAX_BYTES = 20 * 1024 * 1024


class Problem(ValueError):
    pass


def _tools():
    for p in (STYLE, TOOLS):
        if p not in sys.path:
            sys.path.insert(0, p)
    import convert, verify, selftest, check_dupes, build_catalog   # noqa: E401
    return convert, verify, selftest, check_dupes, build_catalog


def _captured(fn, *args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = fn(*args)
    text = re.sub(r"^(ok  |FAIL) +[a-z0-9_-]+/[a-z0-9_-]+ +", "", buf.getvalue().strip())   # the tools' own line prefix
    return rc, text


def _norm(s):
    return "\n".join(l.rstrip() for l in str(s).replace("\r", "").split("\n")).strip("\n")


def _have_all_languages():
    import shutil
    return bool(judge.GPP and judge.JAVAC and judge.JAVA and shutil.which("node"))


def _tidy(q):
    """Small fixes LLM-written JSON often needs: numbers as strings in tests, stray whitespace in ids, and the
    fields a SQL, debugging or SJT question doesn't use (the page still reads them)."""
    kind = q.get("type", "code")
    if kind in ("code", "debug"):
        for t in q.get("samples", []) + q.get("hidden", []):
            if isinstance(t, dict):
                for k in ("in", "out"):
                    if isinstance(t.get(k), (int, float)):
                        t[k] = str(t[k])
                if isinstance(t.get("in"), str) and not t["in"].endswith("\n"):
                    t["in"] += "\n"
    if kind in LABEL and "diff" not in q:
        q["diff"] = LABEL[kind]
    if kind in ("sjt", "repo"):
        for k, v in (("inp", ""), ("out", ""), ("cons", []), ("samples", []), ("hidden", []), ("ref", "")):
            q.setdefault(k, v)
    if kind in ("sql", "debug"):
        q.setdefault("cons", [])
    if isinstance(q.get("id"), str):
        q["id"] = q["id"].strip()
    return q


def _texts(q, keys, errs):
    for k in keys:
        if not isinstance(q.get(k), str) or not q[k].strip():
            errs.append('"%s" is missing' % k)


def _tests_listed(q, errs, warns, shape):
    """samples and hidden are lists of tests; shape(t) says what's wrong with one test, or None."""
    for k in ("samples", "hidden"):
        ts = q.get(k)
        if not isinstance(ts, list) or not ts:
            errs.append('"%s" needs at least 1 test' % k); continue
        bad = [(i, shape(t)) for i, t in enumerate(ts)]
        bad = [(i, why) for i, why in bad if why]
        if bad:
            errs.append('%s test %d: %s' % (k, bad[0][0] + 1, bad[0][1]) + (" (and %d more)" % (len(bad) - 1) if len(bad) > 1 else ""))
    if isinstance(q.get("hidden"), list) and 0 < len(q["hidden"]) < 5:
        warns.append("only %d hidden tests; 8-15 that include edge cases and a maximum-size input work best" % len(q["hidden"]))


def _io_test(t):
    if not (isinstance(t, dict) and isinstance(t.get("in"), str) and isinstance(t.get("out"), str)):
        return 'needs "in" and "out" strings'


SQL_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _sql_format(q, errs, warns):
    _texts(q, ("inp", "out", "ref"), errs)
    schema = q.get("schema")
    if not isinstance(schema, list) or not schema:
        errs.append('"schema" must list the tables: [{"t": "employees", "cols": [["employee_id", "INT"], ["name", "STRING"]]}]')
        return
    tables = {}
    for t in schema:
        ok = isinstance(t, dict) and isinstance(t.get("t"), str) and SQL_NAME.match(t["t"]) and isinstance(t.get("cols"), list) and t["cols"] \
            and all(isinstance(c, list) and len(c) == 2 and all(isinstance(x, str) for x in c) and SQL_NAME.match(c[0]) for c in t["cols"])
        if not ok:
            errs.append('"schema": each table is {"t": name, "cols": [[column, type], ...]} with plain names (letters, digits, _)'); return
        tables[t["t"]] = [c[0] for c in t["cols"]]

    def shape(t):
        if not isinstance(t, dict) or not isinstance(t.get("tables"), dict) or not isinstance(t.get("out"), list):
            return 'needs "tables" ({name: {"cols", "rows"}}) and "out" (the expected rows, a list of lists)'
        if set(t["tables"]) != set(tables):
            return "has tables %s; the schema has %s" % (", ".join(sorted(t["tables"])) or "none", ", ".join(sorted(tables)))
        for name, d in t["tables"].items():
            if not isinstance(d, dict) or d.get("cols") != tables[name]:
                return "table %s: \"cols\" must be %s, as in the schema" % (name, tables[name])
            rows = d.get("rows")
            if not isinstance(rows, list) or not all(isinstance(r, list) and len(r) == len(tables[name]) for r in rows):
                return "table %s: every row needs %d values" % (name, len(tables[name]))
            if not all(v is None or isinstance(v, (str, int, float)) for r in rows for v in r):
                return "table %s: values must be strings, numbers or null" % name
        out = t["out"]
        if not all(isinstance(r, list) for r in out) or len({len(r) for r in out}) > 1:
            return '"out" rows must be lists of the same length'
    _tests_listed(q, errs, warns, shape)


def _debug_format(q, errs, warns):
    _texts(q, ("inp", "out", "starter", "ref"), errs)
    for k in ("pre", "post"):
        if not isinstance(q.get(k), str):
            errs.append('"%s" (the read-only code before / after the editable files) must be a string, "" if none' % k)
    if isinstance(q.get("starter"), str) and q.get("starter") == q.get("ref"):
        errs.append('"starter" (the buggy files) and "ref" (the fixed files) are the same')
    _tests_listed(q, errs, warns, _io_test)
    bugs = q.get("bugs")
    if bugs is None:
        warns.append('no "bugs": list each bug as {"why", "edits": [{"fixed", "buggy"}]} so the checks can prove every one is needed')
    elif not isinstance(bugs, list) or not all(
            isinstance(b, dict) and isinstance(b.get("why"), str) and b["why"].strip() and isinstance(b.get("edits"), list) and b["edits"]
            and all(isinstance(e, dict) and isinstance(e.get("fixed"), str) and e["fixed"] and isinstance(e.get("buggy"), str) for e in b["edits"])
            for b in bugs):
        errs.append('"bugs" must be a list of {"why": "...", "edits": [{"fixed": "text in ref", "buggy": "what the starter has instead"}]}')
    if not q.get("fixnotes"):
        warns.append('no "fixnotes": the report\'s "What was broken" section stays empty')


def _sjt_format(q, errs, warns):
    items = q.get("items")
    if not isinstance(items, list) or not items:
        errs.append('"items" must list the scenarios: [{"lp", "s", "o": [[option, score], ...], "why"}]')


def _repo_format(q, errs, warns, company=None):
    stacks = q.get("stacks")
    if not isinstance(stacks, list) or not stacks or not all(isinstance(s, str) for s in stacks):
        errs.append('"stacks" must list the environments the repository comes in, e.g. ["django"]'); return
    from . import repos
    for s in stacks:
        try:
            repos.src_dir(company, q.get("id"), s)
        except Exception:
            errs.append("data/%s/repos/%s/%s/repo.json is missing. A repository question is a folder (the repo, its fixes, "
                        "hidden tests and repo.json), so it can't be pasted here: see CONTRIBUTING.md" % (company, q.get("id"), s))


def _format(company, q, replace):
    errs, warns = [], []
    if not data.KEY_RE.match(company or ""):
        errs.append("company key must be lowercase letters, digits, - or _ (e.g. google)")
    if not isinstance(q, dict):
        return ["the question must be one JSON object"], warns
    kind = q.get("type", "code")
    if not ID_RE.match(q.get("id") or ""):
        errs.append('"id" must be short, lowercase letters, digits, - or _ (e.g. "maxpath")')
    if kind not in TYPES:
        errs.append('"type" must be one of %s (leave it out for a coding question)' % ", ".join(TYPES))
        return errs, warns
    _texts(q, ("title", "body"), errs)
    if kind == "code":
        if q.get("diff") not in DIFFS:
            errs.append('"diff" must be Easy, Medium or Hard')
        _texts(q, ("inp", "out"), errs)
        _tests_listed(q, errs, warns, _io_test)
        if not q.get("ref"):
            errs.append('"ref" (a Python reference solution) is missing')
    else:
        if q.get("diff") != LABEL[kind]:
            errs.append('"diff" must be "%s" for a %s question' % (LABEL[kind], NAME[kind]))
        if kind == "repo":
            _repo_format(q, errs, warns, company)
        else:
            {"sql": _sql_format, "debug": _debug_format, "sjt": _sjt_format}[kind](q, errs, warns)
    if "cons" in q and not (isinstance(q["cons"], list) and all(isinstance(c, str) for c in q["cons"])):
        errs.append('"cons" must be a list of strings')
    if "year" in q and not (isinstance(q["year"], int) and 2000 <= q["year"] <= 2100):
        errs.append('"year" must be a number like 2026')
    if "month" in q and not (isinstance(q["month"], int) and 1 <= q["month"] <= 12):
        errs.append('"month" must be 1-12')
    if "year" not in q:
        warns.append('no "year": add when it was asked if you know it (the bank sorts by year)')
    if not errs and not replace and os.path.exists(os.path.join(data.DATA_DIR, company, "questions", q["id"] + ".json")):
        errs.append('%s already has a question with id "%s"; pick another id' % (company, q["id"]))
    size = len(json.dumps(q))
    if size > MAX_BYTES:
        errs.append("the question is %.0f MB; keep it under 20 MB (fewer or smaller maximum-size tests)" % (size / 1e6))
    return errs, warns


def check(company, q, replace=False):
    """{ok, checks: [{name, status: ok|warn|fail|skip, detail}], question}. question has stub/driver filled in."""
    convert, verify, selftest, check_dupes, _ = _tools()
    checks = []
    add = lambda name, status, detail="": checks.append({"name": name, "status": status, "detail": detail})
    q = _tidy(dict(q)) if isinstance(q, dict) else q
    errs, warns = _format(company, q, replace)
    add("Format", "fail" if errs else "warn" if warns else "ok", "\n".join(errs + warns) or "all fields present")
    if errs:
        return {"ok": False, "checks": checks, "question": q}
    kind = q.get("type", "code")
    if kind != "code":
        if kind == "repo":
            from . import repos
            for s in q["stacks"]:
                for name, status, detail in repos.verify(company, q["id"], s):
                    add(name, status, detail)
        else:
            {"sql": _check_sql, "debug": _check_debug, "sjt": _check_sjt}[kind](q, add)
        add("Not already in the bank", *_dupes(company, q, check_dupes))
        return {"ok": not any(c["status"] == "fail" for c in checks), "checks": checks, "question": q}
    key = "%s/%s" % (company, q["id"])
    tests = q["samples"] + q["hidden"]

    # function spec -> stub + driver
    spec = None
    try:
        spec = convert.spec_for(key, q)
    except Exception as e:
        add("Function spec", "fail", str(e))
    if spec:
        try:
            before = (q.get("stub"), q.get("driver"))
            convert.apply(q, spec)
            if before[0] is not None and before != (q["stub"], q["driver"]):
                add("Generated code up to date", "fail", '"stub"/"driver" in the file don\'t match its "spec". Don\'t edit them by hand: '
                    "save the question again (the app, or tools/add_question.py <company> <file> --save --replace).")
            add("Function spec", "ok", "%s(%s): stub and input/output driver generated for Python, C++, Java and JavaScript"
                % (spec["fn"], ", ".join(n for n, _ in convert.params(spec))))
        except Exception as e:
            add("Function spec", "fail", "%s: %s" % (type(e).__name__, e)); spec = None
    elif not any(c["name"] == "Function spec" for c in checks):
        if q.get("driver"):
            add("Function spec", "warn", 'no "spec": keeping the hand-written stub and driver')
        else:
            add("Function spec", "warn", 'no "spec": the question is a full program (read stdin, print stdout) in both styles. '
                'Add a "spec" to make it LeetCode-style.')

    # reference solutions
    if spec:
        rc, out = _captured(verify.check, key, spec, q)
        add("Python reference", "fail" if rc else "ok", out)
    else:
        src = q["driver"]["py"]["pre"] + q["ref"] + q["driver"]["py"]["post"] if (q.get("driver") or {}).get("py") else q["ref"]
        res = judge.judge("py", src, [t["in"] for t in tests], 20000)
        add("Python reference", *_verdict(res, tests))
    if q.get("refcpp"):
        if not judge.GPP:
            add("C++ reference", "skip", "no C++ compiler here; the pull-request check runs it")
        else:
            src = q["refcpp"] if q.get("refcppProgram") or "int main" in q["refcpp"] else \
                (q.get("driver") or {}).get("cpp", {}).get("pre", "") + q["refcpp"] + (q.get("driver") or {}).get("cpp", {}).get("post", "")
            add("C++ reference", *_verdict(judge.judge("cpp", src, [t["in"] for t in tests], 10000), tests))

    # 4 languages read the input the same way
    if spec:
        if _have_all_languages():
            rc, out = _captured(selftest.check, key, spec, q)
            add("Drivers in 4 languages", "fail" if rc else "ok", out)
        else:
            add("Drivers in 4 languages", "skip", "needs g++, a JDK and node on this computer; the pull-request check runs it")

    # the tests catch wrong answers
    add("Tests catch wrong answers", *_wrong_answers(q, spec))

    # duplicates
    add("Not already in the bank", *_dupes(company, q, check_dupes))

    ok = not any(c["status"] == "fail" for c in checks)
    return {"ok": ok, "checks": checks, "question": q}


# ------------------------------------------------------------------ SQL, debugging and SJT questions

class NoNode(Exception):
    pass


def _node(req, timeout=600):
    """Runs tools/js_check.js: the page's own SQL engine (AlaSQL) and JavaScript worker, under Node."""
    import shutil
    node = shutil.which("node")
    if not node:
        raise NoNode()
    try:
        r = subprocess.run([node, os.path.join(TOOLS, "js_check.js")], input=json.dumps(req).encode("utf-8"),
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise RuntimeError("tools/js_check.js took over %d s" % timeout)
    if r.returncode:
        raise RuntimeError("tools/js_check.js failed: " + r.stderr.decode("utf-8", "replace")[-500:])
    return json.loads(r.stdout.decode("utf-8"))


NO_NODE = "needs Node.js (node) on this computer to run %s; the pull-request check runs it"


def _short(v, n=160):
    s = json.dumps(v, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + "…"


def _which(tests, ns, bad):
    """'sample 1, hidden 3' for the failing test indexes."""
    names = ["sample %d" % (i + 1) if i < ns else "hidden %d" % (i - ns + 1) for i in bad]
    return ", ".join(names[:6]) + (" and %d more" % (len(names) - 6) if len(names) > 6 else "")


def _distinct_answers(q, key=lambda t: _norm(t["out"])):
    hidden = q["hidden"]
    outs = {key(t) for t in hidden}
    if len(outs) == 1 and len(hidden) > 1:
        return False, "every hidden test expects the same answer (%s), so an answer that always gives it passes. Add tests with other answers." \
            % _short(hidden[0]["out"], 60)
    return True, "hidden tests have %d different answers" % len(outs)


def _check_sql(q, add):
    tests = q["samples"] + q["hidden"]
    ns = len(q["samples"])
    try:
        res = _node({"mode": "sql", "query": q["ref"], "tests": tests})
    except NoNode:
        add("Reference query", "skip", NO_NODE % "the queries in AlaSQL")
        add("Tests catch wrong answers", "skip", NO_NODE % "the queries in AlaSQL")
        return
    bad = [i for i, r in enumerate(res) if not r["ok"]]
    if bad:
        i, r = bad[0], res[bad[0]]
        got = "error: " + r["err"] if "err" in r else "got %d row%s %s" % (len(r["rows"]), "" if len(r["rows"]) == 1 else "s", _short(r["rows"]))
        add("Reference query", "fail", "%d/%d tests give the expected rows. First failure (%s): expected %s, %s"
            % (len(tests) - len(bad), len(tests), _which(tests, ns, [i]), _short(tests[i]["out"]), got))
    else:
        widths = {len(t["out"][0]) for t in tests if t["out"]}
        add("Reference query", "ok", "%d/%d tests give the expected rows in AlaSQL, the engine the page uses%s"
            % (len(tests), len(tests), "" if len(widths) != 1 else " (%d column%s)" % (next(iter(widths)), "" if widths == {1} else "s")))
    canon = lambda t: json.dumps(sorted(json.dumps([round(v, 3) if isinstance(v, float) else v for v in r]) for r in t["out"]))
    distinct, note = _distinct_answers(q, canon)
    if not distinct:
        add("Tests catch wrong answers", "fail", note); return
    empty = sum(1 for t in q["hidden"] if not t["out"])
    notes, status = [note + ("; %d return no rows" % empty if empty else "; none returns an empty result")], "ok"
    wrong = q.get("wrong") or []
    if not wrong:
        status = "warn"
        notes.append('add 1-2 known-wrong queries in "wrong" (e.g. a missing filter, the wrong join or GROUP BY) to prove the tests catch them')
    for w in wrong:
        if not isinstance(w, dict) or not isinstance(w.get("ref"), str) or not w["ref"].strip():
            notes.append('each "wrong" entry needs "ref" (a SQL query) and "why"'); status = "fail"; continue
        r = _node({"mode": "sql", "query": w["ref"], "tests": tests})
        caught = [i for i, x in enumerate(r) if not x["ok"]]
        if caught:
            errs = sum(1 for i in caught if "err" in r[i])
            notes.append("caught: %s (%s on %s)" % (w.get("why", "wrong query"), "error" if errs == len(caught) else "wrong rows", _which(tests, ns, caught)))
        else:
            notes.append("NOT caught: %s gives the expected rows on every test. Add a test it fails." % w.get("why", "a wrong query")); status = "fail"
    add("Tests catch wrong answers", status, "\n".join(notes))


def _js_results(q, code, tests):
    src = q["pre"] + "\n" + code + "\n" + q["post"]          # what the page runs (srcOf in core/util.js)
    res = _node({"mode": "js", "src": src, "inputs": [t["in"] for t in tests], "limit": JS_LIMIT})
    strip = lambda out: _norm("\n".join(l for l in str(out).split("\n") if not l.startswith("[log]")))   # cmpOut
    for t, r in zip(tests, res):
        r["ok"] = not r["tle"] and not r["err"] and strip(r["out"]) == _norm(t["out"])
        r["out"] = strip(r["out"])
    return res


def _first_line(r):
    if r["tle"]:
        return "timed out (%d s)" % (JS_LIMIT // 1000)
    if r["err"]:
        return "error: " + r["err"].strip().splitlines()[0][:200]
    return "printed %s" % _short(r["out"], 200)


def _check_debug(q, add):
    tests = q["samples"] + q["hidden"]
    ns = len(q["samples"])
    names = ("Fixed repository passes", "Starting repository fails", "Each listed bug is needed")
    try:
        fixed = _js_results(q, q["ref"], tests)
    except NoNode:
        for n in names:
            add(n, "skip", NO_NODE % "the repository")
        return
    bad = [i for i, r in enumerate(fixed) if not r["ok"]]
    if bad:
        i = bad[0]
        add(names[0], "fail", "%d/%d tests pass with the fixed files (\"ref\"). First failure (%s): expected %s, %s"
            % (len(tests) - len(bad), len(tests), _which(tests, ns, [i]), _short(tests[i]["out"], 200), _first_line(fixed[i])))
        for n in names[1:]:
            add(n, "skip", "runs once the fixed files pass every test")
        return
    add(names[0], "ok", "%d/%d tests pass with the fixed files (\"ref\"), slowest %.0f ms" % (len(tests), len(tests), max(r["ms"] for r in fixed)))
    start = _js_results(q, q["starter"], tests)
    caught = [i for i, r in enumerate(start) if not r["ok"]]
    if not caught:
        add(names[1], "fail", "the buggy files (\"starter\") pass every test, so there's nothing to debug. Add tests that show the bugs.")
    else:
        fs = sum(1 for i in caught if i < ns)
        add(names[1], "ok", "the buggy files (\"starter\") fail %d/%d tests (%d of %d samples): %s"
            % (len(caught), len(tests), fs, ns, _which(tests, ns, caught)))
    # each bug, put back into the fixed files on its own, must fail a test
    bugs = q.get("bugs") or []
    if not bugs:
        add(names[2], "warn", 'no "bugs" listed. List each as {"why", "edits": [{"fixed": "text in ref", "buggy": "the starter\'s version"}]}: '
            "the check puts each bug back into the fixed files on its own and makes sure a test fails.")
    else:
        notes, status, all_back = [], "ok", q["ref"]
        for b in bugs:
            code, missing = q["ref"], None
            for e in b["edits"]:
                n = code.count(e["fixed"])
                if n != 1:
                    missing = "%s in the fixed files: %s" % ("not found" if n == 0 else "found %d times (make it longer so it's unique)" % n, _short(e["fixed"], 80))
                    break
                code = code.replace(e["fixed"], e["buggy"])
                all_back = all_back.replace(e["fixed"], e["buggy"], 1)
            if missing:
                notes.append("can't apply: %s: %s" % (b["why"], missing)); status = "fail"; continue
            r = _js_results(q, code, tests)
            hit = [i for i, x in enumerate(r) if not x["ok"]]
            if hit:
                notes.append("needed: %s (fails %s)" % (b["why"], _which(tests, ns, hit)))
            else:
                notes.append("NOT needed: %s: with only this bug every test passes. Add a test it fails, or drop it from the list." % b["why"]); status = "fail"
        if status == "fail":
            n = sum(1 for x in notes if not x.startswith("needed:"))
            notes.insert(0, "%d of the %d listed bugs %s a problem:" % (n, len(bugs), "has" if n == 1 else "have"))
            notes.sort(key=lambda x: x.startswith("needed:"))
        if status == "ok":
            if _norm(all_back) == _norm(q["starter"]):
                notes.insert(0, "all %d bugs are caught one at a time, and putting them all back gives the starting files exactly" % len(bugs))
            else:
                status = "warn"
                notes.insert(0, "all %d bugs are caught one at a time, but putting them all back doesn't give the starting files: "
                                "is a bug missing from the list? (fine if the starter only differs in comments)" % len(bugs))
        add(names[2], status, "\n".join(notes))
    distinct, note = _distinct_answers(q)
    add("Tests catch wrong answers", "ok" if distinct else "fail", note)


def _check_sjt(q, add):
    errs, warns = [], []
    seen, best_at = set(), []
    for n, it in enumerate(q["items"], 1):
        where = "scenario %d" % n
        if not isinstance(it, dict):
            errs.append(where + ": must be an object"); continue
        for k, what in (("s", "the scenario"), ("why", "why the best answer is best"), ("lp", "the principle or skill it tests")):
            if not isinstance(it.get(k), str) or not it[k].strip():
                errs.append('%s: "%s" (%s) is missing' % (where, k, what))
        o = it.get("o")
        if not isinstance(o, list) or not all(isinstance(x, list) and len(x) == 2 and isinstance(x[0], str) and x[0].strip() for x in o):
            errs.append('%s: "o" must be a list of [option text, score]' % where); continue
        if not 3 <= len(o) <= 6:
            errs.append("%s: has %d options; give 3-6" % (where, len(o)))
        if not all(isinstance(x[1], int) and not isinstance(x[1], bool) and x[1] in (0, 1, 2) for x in o):
            errs.append("%s: every option needs a score: 2 best, 1 partly good, 0 weak" % where)
        else:
            nb = sum(1 for x in o if x[1] == 2)
            if nb != 1:
                errs.append("%s: has %d best answers (score 2); it needs exactly one" % (where, nb))
            else:
                best_at.append(next(i for i, x in enumerate(o) if x[1] == 2))
        texts = [x[0].strip().lower() for x in o]
        if len(set(texts)) < len(texts):
            errs.append("%s: two options have the same text" % where)
        s = (it.get("s") or "").strip().lower()
        if s and s in seen:
            errs.append("%s: the same scenario appears twice" % where)
        seen.add(s)
    items = q["items"]
    if len(items) < 5:
        warns.append("only %d scenario%s; a section usually has 8-15" % (len(items), "" if len(items) == 1 else "s"))
    if len(best_at) >= 4:
        top = max(set(best_at), key=best_at.count)
        if best_at.count(top) > len(best_at) / 2:
            warns.append("the best answer is option %d in %d of %d scenarios; shuffle the options so its place doesn't give it away"
                         % (top + 1, best_at.count(top), len(best_at)))
    if errs:
        add("Scenarios", "fail", "\n".join(errs + warns))
    else:
        add("Scenarios", "warn" if warns else "ok", "\n".join(
            ["%d scenarios, each with %s options, exactly one best answer (2 points), every option scored, and a reason"
             % (len(items), "-".join(str(x) for x in sorted({min(len(i["o"]) for i in items), max(len(i["o"]) for i in items)})))] + warns))


def _verdict(res, tests):
    if "compile_error" in res:
        return "fail", "compile error:\n" + res["compile_error"][-1500:]
    bad = [i for i, (t, r) in enumerate(zip(tests, res["results"])) if r["tle"] or r["err"] or _norm(r["out"]) != _norm(t["out"])]
    slow = max(r["ms"] for r in res["results"])
    if bad:
        r, t = res["results"][bad[0]], tests[bad[0]]
        return "fail", "%d/%d tests pass. First failure (test %d): expected %r, got %r %s" % (
            len(tests) - len(bad), len(tests), bad[0] + 1, t["out"][:120], r["out"][:120], r["err"][-300:])
    return "ok", "%d/%d tests pass, slowest %.0f ms" % (len(tests), len(tests), slow)


def _wrong_answers(q, spec):
    hidden = q["hidden"]
    outs = {_norm(t["out"]) for t in hidden}
    if len(outs) == 1 and len(hidden) > 1:
        return "fail", "every hidden test expects %r, so a program that always prints that passes. Add tests with other answers." % next(iter(outs))[:60]
    notes, status = [], "ok"
    biggest = max(len(t["in"]) for t in hidden)
    notes.append("hidden tests have %d different answers; the largest input is %s" % (
        len(outs), "%.0f KB" % (biggest / 1e3) if biggest > 2000 else "%d characters" % biggest))
    wrong = q.get("wrong") or []
    if not wrong:
        status = "warn"
        notes.append('add 1-2 known-wrong solutions in "wrong" (e.g. brute force, off-by-one) to prove the tests catch them')
    for w in wrong:
        if not isinstance(w, dict) or not w.get("ref"):
            notes.append('each "wrong" entry needs "ref" (Python, same shape as "ref") and "why"'); status = "fail"; continue
        code = w["ref"]
        if spec and "class Solution" in code:
            code = q["driver"]["py"]["pre"] + code + q["driver"]["py"]["post"]
        res = judge.judge("py", code, [t["in"] for t in q["samples"] + hidden], PY_LIMIT)
        if "compile_error" in res:
            notes.append("wrong solution (%s) doesn't run: %s" % (w.get("why", "?"), res["compile_error"][-200:])); status = "fail"; continue
        tests = q["samples"] + hidden
        caught = [i for i, (t, r) in enumerate(zip(tests, res["results"])) if r["tle"] or r["err"] or _norm(r["out"]) != _norm(t["out"])]
        if caught:
            how = "too slow" if any(res["results"][i]["tle"] for i in caught) else "wrong answer"
            notes.append("caught: %s (%s on %d test%s)" % (w.get("why", "wrong solution"), how, len(caught), "" if len(caught) == 1 else "s"))
        else:
            notes.append("NOT caught: %s passes every test. Add a test it fails." % w.get("why", "a wrong solution")); status = "fail"
    return status, "\n".join(notes)


def _dupes(company, q, check_dupes):
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, company, "questions"))
        p = os.path.join(d, company, "questions", q["id"] + ".json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump(q, f)
        a = check_dupes.load(p)
    import glob
    paths = sorted(glob.glob(os.path.join(data.DATA_DIR, "*", "questions", "*.json")))
    bank = [check_dupes.load(x) for x in paths]
    companies = sorted({b["_key"].split("/")[0] for b in bank})
    found = []
    for b in bank:
        if b["_key"] == a["_key"]:
            continue
        level, j, why = check_dupes.compare(a, b)
        if level:
            found.append((level, j, b, why, check_dupes.settled(a, b)))
    where = "checked against %d questions from %s on this computer" % (len(bank), ", ".join(companies) or "no company")
    dup = [f for f in found if f[0] == "duplicate" and not f[4]]
    lines = ["%s %s %r (overlap %.2f%s)" % (lv, b["_key"], b.get("title", ""), j, ", " + ", ".join(w) if w else "")
             for lv, j, b, w, ok in sorted(found, key=lambda f: -f[1]) if not ok]
    if dup:
        return "fail", "\n".join(lines) + '\nThe same question? Add "alsoSeen": ["company/id"] instead of a copy. ' \
            'A different problem? Add "distinctFrom": ["company/id"].\n' + where
    if lines:
        return "warn", "\n".join(lines) + "\nLook at these; if one is the same question add \"alsoSeen\", otherwise \"distinctFrom\".\n" + where
    return "ok", where


def new_company_config(company, name, tagline=""):
    name = (name or company.title()).strip()
    return {
        "key": company, "name": name if name.lower().endswith("oa mock") else name + " OA Mock",
        "tagline": tagline or "Coding questions", "headline": "Sit a timed %s OA, then see what passed." % name,
        "blurb": "questions reported from %s OAs" % name, "defaultFmt": "oa", "custom": [],
        "formats": {
            "oa": {"name": "OA", "desc": "Easy, Medium and Hard coding questions · 90 min", "mins": 90, "pools": ["Easy", "Medium", "Hard"]},
            "custom": {"name": "Custom", "desc": "Pick the questions and the time", "mins": 60, "pools": []},
        },
        "offlist": [], "order": [],
    }


def save(company, q, name=None, tagline=None, replace=False):
    """Writes the question (after check() passed) and, for a new company, its company.json. Returns the paths."""
    res = check(company, q, replace=replace)
    if not res["ok"]:
        raise Problem("the question doesn't pass the checks yet")
    q = res["question"]
    d = os.path.join(data.DATA_DIR, company)
    written = []
    os.makedirs(os.path.join(d, "questions"), exist_ok=True)
    cfg = os.path.join(d, "company.json")
    if not os.path.exists(cfg):
        with open(cfg, "w", encoding="utf-8") as f:
            json.dump(new_company_config(company, name, tagline), f, indent=2, ensure_ascii=False); f.write("\n")
        written.append(cfg)
    path = os.path.join(d, "questions", q["id"] + ".json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(q, f, indent=1, ensure_ascii=False)
    written.append(path)
    _, _, _, _, build_catalog = _tools()
    cat = build_catalog.build()
    with open(build_catalog.OUT, "w", encoding="utf-8") as f:
        f.write(json.dumps(cat, indent=1, ensure_ascii=False) + "\n")
    written.append(build_catalog.OUT)
    return [os.path.relpath(p, data.ROOT).replace(os.sep, "/") for p in written]


# ------------------------------------------------------------------ pull requests

def _run(args, timeout=120, env=None, inp=None):
    r = subprocess.run(args, cwd=data.ROOT, input=inp, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout,
                       env=dict(os.environ, GIT_TERMINAL_PROMPT="0", **(env or {})))
    return r.returncode, r.stdout.decode("utf-8", "replace").strip(), r.stderr.decode("utf-8", "replace").strip()


def upstream():
    """owner/repo of the origin remote on GitHub (where pull requests go)."""
    rc, url, _ = _run(["git", "remote", "get-url", "origin"], 10)
    m = re.search(r"github\.com[:/]+([^/]+)/([^/]+?)(?:\.git)?/?$", url) if rc == 0 else None
    return "%s/%s" % (m.group(1), m.group(2)) if m else None


def share_status():
    """What sending a pull request from here needs, and whether it's there."""
    st = library.git_state()
    out = {"git": st.get("git"), "upstream": upstream() if st.get("git") else None, "gh": False, "login": None}
    try:
        rc, _, _ = _run(["gh", "--version"], 10)
        out["gh"] = rc == 0
    except OSError:
        pass
    if out["gh"]:
        rc, login, _ = _run(["gh", "api", "user", "-q", ".login"], 20)
        out["login"] = login if rc == 0 and login else None
    return out


def _catalog_with(build_catalog, base_text, company):
    """GitHub's catalog with only this company's entry recomputed from the files here. Each company's entry is
    on its own lines, so pull requests for different companies merge without conflicts."""
    try:
        cat = json.loads(base_text) if base_text else {"version": 1, "companies": []}
    except ValueError:
        cat = {"version": 1, "companies": []}
    entries = {c["key"]: c for c in cat.get("companies", [])}
    entries[company] = build_catalog.entry(company)
    cat["companies"] = [entries[k] for k in sorted(entries)]
    return json.dumps(cat, indent=1, ensure_ascii=False) + "\n"


def share(company, qid, note=""):
    """Opens a pull request with data/<company>/questions/<qid>.json (+ company.json if the company is new)."""
    if not (data.KEY_RE.match(company or "") and ID_RE.match(qid or "")):
        raise Problem("bad company or question id")
    qpath = "data/%s/questions/%s.json" % (company, qid)
    if not os.path.isfile(os.path.join(data.ROOT, qpath)):
        raise Problem("save the question first")
    st = share_status()
    if not st["git"] or not st["upstream"]:
        raise Problem("this copy isn't a git clone of the GitHub repository")
    if not st["gh"]:
        raise Problem("the GitHub CLI (gh) isn't installed")
    if not st["login"]:
        raise Problem("the GitHub CLI isn't signed in: run  gh auth login  in a terminal, then try again")
    login, up = st["login"], st["upstream"]
    with open(os.path.join(data.ROOT, qpath), encoding="utf-8") as f:
        q = json.load(f)
    res = check(company, q, replace=True)
    if not res["ok"]:
        raise Problem("the question doesn't pass the checks: fix it and save again")
    log = []
    def git(*args, **kw):
        rc, out, err = _run(["git"] + list(args), **kw)
        log.append("$ git " + " ".join(args) + ("\n" + (out or err)[-500:] if (out or err) else ""))
        if rc:
            raise Problem("git %s failed: %s" % (args[0], (err or out).splitlines()[-1] if (err or out) else rc))
        return out
    git("fetch", "--quiet", "origin", timeout=300)
    base = "origin/main"
    files = {qpath: open(os.path.join(data.ROOT, qpath), "rb").read()}
    cfg = "data/%s/company.json" % company
    new_company = subprocess.run(["git", "cat-file", "-e", "%s:%s" % (base, cfg)], cwd=data.ROOT,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0
    if new_company:
        files[cfg] = open(os.path.join(data.ROOT, cfg), "rb").read()
    _, _, _, _, build_catalog = _tools()
    rc, base_cat, _ = _run(["git", "show", base + ":data/catalog.json"], 60)
    files["data/catalog.json"] = _catalog_with(build_catalog, base_cat if rc == 0 else "", company).encode("utf-8")

    # a commit on top of GitHub's main with just these files, built in a temporary index (your files stay as they are)
    with tempfile.TemporaryDirectory() as tmp:
        env = {"GIT_INDEX_FILE": os.path.join(tmp, "index")}
        git("read-tree", base, env=env)
        for path, blob in files.items():
            sha = git("hash-object", "-w", "--stdin", inp=blob)
            git("update-index", "--add", "--cacheinfo", "100644,%s,%s" % (sha, path), env=env)
        tree = git("write-tree", env=env)
    name = _run(["git", "config", "user.name"], 10)[1] or login
    email = _run(["git", "config", "user.email"], 10)[1] or "%s@users.noreply.github.com" % login
    who = {"GIT_AUTHOR_NAME": name, "GIT_AUTHOR_EMAIL": email, "GIT_COMMITTER_NAME": name, "GIT_COMMITTER_EMAIL": email}
    title = "Add %s/%s: %s" % (company, qid, q.get("title", qid))
    commit = git("commit-tree", tree, "-p", base, "-m", title, env=who)

    branch = "add-%s-%s-%s" % (company, qid, time.strftime("%Y%m%d%H%M%S"))
    owner = up.split("/")[0]
    if login.lower() == owner.lower():
        target, head = up, branch
    else:
        rc, fork, err = _run(["gh", "api", "-X", "POST", "repos/%s/forks" % up, "-q", ".full_name"], 120)
        if rc or not fork:
            raise Problem("couldn't fork %s: %s" % (up, err[-300:]))
        log.append("fork: " + fork)
        target, head = fork, "%s:%s" % (fork.split("/")[0], branch)
    url = "https://github.com/%s.git" % target
    for attempt in range(6):          # a brand-new fork can take a few seconds to accept pushes
        rc, out, err = _run(["git", "-c", "credential.helper=", "-c", "credential.helper=!gh auth git-credential",
                             "push", url, "%s:refs/heads/%s" % (commit, branch)], 300)
        if rc == 0:
            break
        time.sleep(4)
    else:
        raise Problem("couldn't push to %s: %s" % (target, err.splitlines()[-1] if err else rc))
    log.append("pushed %s to %s" % (branch, target))
    summary = "\n".join("- %s: %s" % (c["name"], c["status"]) for c in res["checks"])
    src = ", ".join("%s: %s" % (k, q[k]) for k in ("src", "year", "month", "college", "role") if q.get(k))
    body = ("Adds **%s** to %s%s.\n\n%s\n\nSource: %s\n\nLocal checks:\n%s\n\n_Sent from the OA Mock app._"
            % (q.get("title", qid), company, " (new company)" if new_company else "", note.strip(), src or "not given", summary))
    rc, pr, err = _run(["gh", "pr", "create", "--repo", up, "--base", "main", "--head", head, "--title", title, "--body", body], 120)
    if rc:
        raise Problem("pushed the branch, but couldn't open the pull request: %s" % (err.splitlines()[-1] if err else rc))
    return {"url": pr.splitlines()[-1], "branch": branch, "log": "\n".join(log)}
