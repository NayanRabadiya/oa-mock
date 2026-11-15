"""Environments for repository questions: the frameworks a repo runs on (Django today; Node.js and Spring Boot next).

Each environment is described in app/envs/<key>/env.json and installs into .oa-cache/envs/<key>/, a private folder
of the app, so nothing is installed system-wide and removing it frees the space again.

  status()                {envs: {key: {name, state, plan, ...}}, job}
  start("install", key)   sets it up in the background (job with a live log)
  start("cancel")         stops the running setup
  remove(key)             deletes the folder
  python(key)             the interpreter to run a Django project with, once it's ready

States: ready · missing (can be set up) · outdated (the pinned packages changed since it was set up; set up again) ·
blocked (something it needs, like a new enough Python, isn't on this computer; `plan.why` says what to do).
"""
import hashlib, json, os, shutil, signal, subprocess, sys, threading, time

from . import data, submissions

ENV_SRC = os.path.join(data.ROOT, "app", "envs")
ENV_DIR = os.path.join(submissions.CACHE_DIR, "envs")
IS_WIN, IS_MAC = os.name == "nt", sys.platform == "darwin"
TIMEOUT_S = 20 * 60
KEYS = ("django",)                     # node and spring arrive with their repos
MIN_PY = (3, 10)

_job = {"id": 0, "state": "idle"}
_proc = None
_lock = threading.Lock()
_py_cache = {}


def _manifest(key):
    with open(os.path.join(ENV_SRC, key, "env.json"), encoding="utf-8") as f:
        return json.load(f)


def _req_hash(key):
    with open(os.path.join(ENV_SRC, key, "requirements.txt"), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def _venv_python(key):
    d = os.path.join(ENV_DIR, key, "venv")
    return os.path.join(d, "Scripts", "python.exe") if IS_WIN else os.path.join(d, "bin", "python")


def _py_version(exe):
    try:
        out = subprocess.run([exe, "-c", "import sys; print('%d.%d.%d' % sys.version_info[:3])"], stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL, timeout=10).stdout.decode().strip()
        return tuple(int(x) for x in out.split(".")) if out else None
    except Exception:
        return None


def base_python():
    """A Python 3.10+ to build the Django environment from: (path, version) or (None, best version seen)."""
    hit = _py_cache.get("py")
    if hit and time.time() - hit[0] < 60:
        return hit[1]
    cands = [sys.executable]
    names = ["python3.%d" % m for m in range(14, 9, -1)] + ["python3", "python"]
    for n in names:
        p = shutil.which(n)
        if p:
            cands.append(p)
    if IS_MAC:
        for m in range(14, 9, -1):
            cands += ["/opt/homebrew/bin/python3.%d" % m, "/usr/local/bin/python3.%d" % m,
                      "/Library/Frameworks/Python.framework/Versions/3.%d/bin/python3" % m]
    if IS_WIN and shutil.which("py"):
        cands.append("py")
    best, seen = None, None
    for c in dict.fromkeys(cands):
        if c != "py" and not os.path.isfile(c):
            continue
        v = _py_version(c) if c != "py" else _py_launcher_version()
        if not v:
            continue
        seen = max(seen or v, v)
        if v[:2] >= MIN_PY and (best is None or v > best[1]):
            best = (c, v)
    res = best or (None, seen)
    _py_cache["py"] = (time.time(), res)
    return res


def _py_launcher_version():
    v = _py_version_cmd(["py", "-3", "-c", "import sys; print('%d.%d.%d' % sys.version_info[:3])"])
    return v


def _py_version_cmd(cmd):
    try:
        out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=10).stdout.decode().strip()
        return tuple(int(x) for x in out.split(".")) if out else None
    except Exception:
        return None


def _state(key):
    marker = os.path.join(ENV_DIR, key, "ready.json")
    if os.path.isfile(marker) and os.path.isfile(_venv_python(key)):
        try:
            with open(marker, encoding="utf-8") as f:
                m = json.load(f)
        except ValueError:
            m = {}
        return ("ready" if m.get("requirements") == _req_hash(key) else "outdated"), m
    return "missing", {}


def _disk_mb(key):
    total = 0
    for root, _, files in os.walk(os.path.join(ENV_DIR, key)):
        for f in files:
            try:
                st = os.lstat(os.path.join(root, f))          # like du: blocks on disk, symlinks not followed
                total += st.st_blocks * 512 if hasattr(st, "st_blocks") else st.st_size
            except OSError:
                pass
    return round(total / 1e6)


def plan(key):
    """What setting it up here needs: {can, uses?, why?, how?}."""
    if key == "django":
        exe, ver = base_python()
        if exe:
            return {"can": True, "uses": "Python %s" % ".".join(map(str, ver))}
        found = (" This computer has Python %s." % ".".join(map(str, ver[:2]))) if ver else ""
        if IS_MAC:
            how = "Install Python 3.12 from python.org/downloads (or run  brew install python@3.12  if you use Homebrew), then try again."
        elif IS_WIN:
            how = "Install Python 3.12 with  winget install Python.Python.3.12  (or from python.org), then try again."
        else:
            how = "Install python3.12 (or any Python 3.10+) with your package manager, then try again."
        return {"can": False, "why": "Django 5.2 needs Python 3.10 or newer." + found, "how": how}
    return {"can": False, "why": "Not available yet."}


def status():
    envs = {}
    for key in KEYS:
        m = _manifest(key)
        st, marker = _state(key)
        e = {k: m.get(k) for k in ("name", "short", "lang", "summary", "needs", "download_mb", "disk_mb", "minutes", "test_command")}
        e["state"] = st
        if st == "ready":
            e["installed"] = marker.get("versions", {})
            e["size_mb"] = marker.get("size_mb")
        else:
            p = plan(key)
            e["plan"] = p
            if not p["can"]:
                e["state"] = "blocked"
        envs[key] = e
    return {"envs": envs, "job": job()}


def ready(key):
    return key in KEYS and _state(key)[0] == "ready"


def python(key):
    return _venv_python(key)


def job():
    with _lock:
        return dict(_job)


def _say(line):
    with _lock:
        _job["log"] = (_job.get("log", "") + line.rstrip() + "\n")[-12000:]


def _step(args, title, cwd=None):
    """Runs one command, streaming its output into the job log. Returns its exit code."""
    global _proc
    _say("$ " + title)
    extra = {"creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0)} if IS_WIN else {"start_new_session": True}
    env = dict(os.environ, PIP_DISABLE_PIP_VERSION_CHECK="1", PIP_NO_INPUT="1", PYTHONUNBUFFERED="1")
    p = subprocess.Popen(args, cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, **extra)
    with _lock:
        _proc = p
    for raw in iter(p.stdout.readline, b""):
        line = raw.decode("utf-8", "replace").rstrip().split("\r")[-1]
        if line.strip():
            _say(line)
        with _lock:
            if _job.get("cancelled"):
                break
    try:
        rc = p.wait(timeout=5)
    except subprocess.TimeoutExpired:
        _stop(p); rc = p.wait()
    with _lock:
        _proc = None
    return rc


def _install_django(key):
    exe, ver = base_python()
    if not exe:
        raise RuntimeError(plan(key)["why"])
    d = os.path.join(ENV_DIR, key)
    shutil.rmtree(d, ignore_errors=True)          # an old or half-built one; "ready" is only written at the end
    os.makedirs(d)
    base = [exe] if exe != "py" else ["py", "-3"]
    if _step(base + ["-m", "venv", os.path.join(d, "venv")], "python -m venv  (Python %s)" % ".".join(map(str, ver))):
        raise RuntimeError("Couldn't create the Python environment (python -m venv). On Debian or Ubuntu, install python3-venv.")
    py = _venv_python(key)
    req = os.path.join(ENV_SRC, key, "requirements.txt")
    if _step([py, "-m", "pip", "install", "--progress-bar", "off", "-r", req], "pip install -r requirements.txt"):
        raise RuntimeError("pip couldn't install the packages. Check your internet connection and try again.")
    out = subprocess.run([py, "-c", "import django, rest_framework; print(django.get_version(), rest_framework.VERSION)"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
    if out.returncode:
        raise RuntimeError("The packages installed, but Django doesn't start: " + out.stderr.decode()[-300:])
    dj, drf = out.stdout.decode().split()
    marker = {"requirements": _req_hash(key), "versions": {"Python": ".".join(map(str, ver)), "Django": dj, "Django REST framework": drf},
              "at": time.time()}
    marker["size_mb"] = _disk_mb(key)
    with open(os.path.join(d, "ready.json"), "w", encoding="utf-8") as f:
        json.dump(marker, f)
    _say("Ready: Django %s, Django REST framework %s (%d MB)" % (dj, drf, marker["size_mb"]))


def _run(key):
    err = None
    try:
        {"django": _install_django}[key](key)
    except Exception as e:
        err = str(e)
    with _lock:
        if _job.get("cancelled"):
            err = "Cancelled."
        _job.update(state="failed" if err else "done", finished=time.time())
        if err:
            _job["error"] = err
    if err:
        shutil.rmtree(os.path.join(ENV_DIR, key), ignore_errors=True)


def _stop(p):
    try:
        if IS_WIN:
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            os.killpg(p.pid, signal.SIGTERM)
    except Exception:
        try: p.terminate()
        except Exception: pass


def start(action, key=None):
    if action == "cancel":
        with _lock:
            if _job.get("state") != "running":
                raise ValueError("nothing is being set up")
            _job["cancelled"] = True
            p = _proc
        if p:
            _stop(p)
        return job()
    if action != "install":
        raise ValueError("unknown action")
    if key not in KEYS:
        raise ValueError("unknown environment")
    if ready(key):
        raise ValueError("%s is already set up" % _manifest(key)["name"])
    p = plan(key)
    if not p["can"]:
        raise ValueError(p["why"] + " " + p.get("how", ""))
    with _lock:
        if _job.get("state") == "running":
            raise ValueError("another environment is still being set up")
        _job.clear()
        _job.update(id=int(time.time() * 1000), key=key, state="running", log="", started=time.time())
        snap = dict(_job)
    threading.Thread(target=_run, args=(key,), daemon=True).start()
    return snap


def remove(key):
    if key not in KEYS:
        raise ValueError("unknown environment")
    with _lock:
        if _job.get("state") == "running" and _job.get("key") == key:
            raise ValueError("it's being set up right now")
    shutil.rmtree(os.path.join(ENV_DIR, key), ignore_errors=True)
    return status()
