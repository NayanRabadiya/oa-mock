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

from . import data, judge, submissions

ENV_SRC = os.path.join(data.ROOT, "app", "envs")
ENV_DIR = os.path.join(submissions.CACHE_DIR, "envs")
IS_WIN, IS_MAC = os.name == "nt", sys.platform == "darwin"
TIMEOUT_S = 20 * 60
KEYS = ("node", "django", "spring")
MIN_PY = (3, 10)
MIN_NODE = 18
MIN_JAVA = 17
PIN = {"django": "requirements.txt", "node": "package-lock.json", "spring": "template/pom.xml"}   # changing it asks for a new setup

_job = {"id": 0, "state": "idle"}
_proc = None
_lock = threading.Lock()
_py_cache = {}


def _manifest(key):
    with open(os.path.join(ENV_SRC, key, "env.json"), encoding="utf-8") as f:
        return json.load(f)


def _req_hash(key):
    with open(os.path.join(ENV_SRC, key, PIN[key]), "rb") as f:
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


def node_tools():
    """(node, npm, version) of a Node.js 18+ on this computer, or (None, None, best version seen)."""
    hit = _py_cache.get("node")
    if hit and time.time() - hit[0] < 60:
        return hit[1]
    cands = [shutil.which("node")]
    if IS_MAC:
        cands += ["/opt/homebrew/bin/node", "/usr/local/bin/node"]
    if IS_WIN:
        cands += [os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "nodejs", "node.exe")]
    res = (None, None, None)
    for c in dict.fromkeys(x for x in cands if x and os.path.isfile(x)):
        v = _py_version_cmd([c, "-e", "console.log(process.versions.node)"])
        if not v:
            continue
        d = os.path.dirname(c)
        npm = next((p for p in (os.path.join(d, "npm.cmd" if IS_WIN else "npm"), shutil.which("npm")) if p and os.path.isfile(p)), None)
        if v[0] >= MIN_NODE and npm:
            res = (c, npm, v); break
        if not res[2] or v > res[2]:
            res = (None, None, v)
    _py_cache["node"] = (time.time(), res)
    return res


def node_env(key="node"):
    """Environment variables for running a Node repository's tests with this environment."""
    d = os.path.join(ENV_DIR, key)
    return {"NODE_PATH": os.path.join(d, "node_modules"), "MONGOMS_DOWNLOAD_DIR": os.path.join(d, "mongodb-binaries"),
            "MONGOMS_PREFER_GLOBAL_PATH": "0"}


def java_tools():
    """(java, JAVA_HOME, major version) of a JDK 17+ (the one the app found for Java answers), or (None, None, best seen)."""
    hit = _py_cache.get("java")
    if hit and time.time() - hit[0] < 60:
        return hit[1]
    res = (None, None, None)
    if judge.JAVAC and judge.JAVA:
        try:
            p = subprocess.run([judge.JAVA, "-version"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=20)
            import re
            m = re.search(r'version "(\d+)(?:\.(\d+))?', p.stdout.decode("utf-8", "replace"))
            major = int(m.group(1)) if m else 0
            if major == 1 and m.group(2):
                major = int(m.group(2))
            home = os.path.dirname(os.path.dirname(os.path.realpath(judge.JAVAC)))
            res = (judge.JAVA, home, major) if major >= MIN_JAVA else (None, None, major)
        except Exception:
            pass
    _py_cache["java"] = (time.time(), res)
    return res


def maven(key="spring"):
    d = os.path.join(ENV_DIR, key, "maven", "bin")
    return os.path.join(d, "mvn.cmd" if IS_WIN else "mvn")


def spring_env(key="spring"):
    _, home, _ = java_tools()
    env = {"MAVEN_OPTS": "-Xmx768m -XX:+UseSerialGC -XX:TieredStopAtLevel=1"}
    if home:
        env["JAVA_HOME"] = home
    return env


def maven_args(key="spring"):
    return ["-B", "-ntp", "-Dstyle.color=never", "-Dmaven.repo.local=" + os.path.join(ENV_DIR, key, "m2")]


def _ready_file(key):
    if key == "spring":
        return maven(key)
    if key == "node":
        return os.path.join(ENV_DIR, key, "node_modules", "jest", "bin", "jest.js")
    return _venv_python(key)


def _state(key):
    marker = os.path.join(ENV_DIR, key, "ready.json")
    if os.path.isfile(marker) and os.path.isfile(_ready_file(key)):
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
    if key == "node":
        node, npm, ver = node_tools()
        if node:
            return {"can": True, "uses": "Node.js %s" % ".".join(map(str, ver))}
        found = (" This computer has Node.js %s." % ".".join(map(str, ver))) if ver else ""
        how = ("Install Node.js 22 LTS from nodejs.org (or  brew install node  with Homebrew), then try again." if IS_MAC else
               "Install Node.js 22 LTS with  winget install OpenJS.NodeJS.LTS  (or from nodejs.org), then try again." if IS_WIN else
               "Install Node.js 18 or newer (nodejs.org, or your package manager's nodejs and npm), then try again.")
        return {"can": False, "why": "The Node.js environment needs Node.js %d or newer with npm." % MIN_NODE + found, "how": how}
    if key == "spring":
        java, home, major = java_tools()
        if java:
            return {"can": True, "uses": "Java %d" % major}
        found = (" This computer has Java %d." % major) if major else ""
        return {"can": False, "why": "Spring Boot 3 needs Java %d or newer (a JDK)." % MIN_JAVA + found,
                "how": "Install Java from the app's language menu (the download icon next to Java), then try again."}
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


def _step(args, title, cwd=None, env=None):
    """Runs one command, streaming its output into the job log. Returns its exit code."""
    global _proc
    _say("$ " + title)
    extra = {"creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0)} if IS_WIN else {"start_new_session": True}
    env = dict(os.environ, PIP_DISABLE_PIP_VERSION_CHECK="1", PIP_NO_INPUT="1", PYTHONUNBUFFERED="1", **(env or {}))
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


def _install_node(key):
    node, npm, ver = node_tools()
    if not node:
        raise RuntimeError(plan(key)["why"])
    d = os.path.join(ENV_DIR, key)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    for f in ("package.json", "package-lock.json"):
        shutil.copyfile(os.path.join(ENV_SRC, key, f), os.path.join(d, f))
    env = node_env(key)
    if _step([npm, "ci", "--no-audit", "--no-fund", "--loglevel=warn"], "npm ci  (Node.js %s; also downloads MongoDB for the tests)" % ".".join(map(str, ver)),
             cwd=d, env=env):
        raise RuntimeError("npm couldn't install the packages. Check your internet connection and try again.")
    check = ("const {MongoMemoryServer}=require('mongodb-memory-server');"
             "MongoMemoryServer.create().then(async s=>{await s.stop();"
             "console.log('MongoDB starts: '+(require('mongodb-memory-server-core/package.json').version))})"
             ".catch(e=>{console.error(e.message);process.exit(1)})")
    if _step([node, "-e", check], "start the in-memory MongoDB once", cwd=d, env=env):
        raise RuntimeError("The packages installed, but the in-memory MongoDB doesn't start here (see Details).")
    vers = {"Node.js": ".".join(map(str, ver))}
    for pkg, label in (("express", "Express"), ("mongoose", "Mongoose"), ("jest", "Jest")):
        try:
            with open(os.path.join(d, "node_modules", pkg, "package.json"), encoding="utf-8") as f:
                vers[label] = json.load(f)["version"]
        except (OSError, ValueError, KeyError):
            pass
    marker = {"requirements": _req_hash(key), "versions": vers, "at": time.time(), "size_mb": _disk_mb(key)}
    with open(os.path.join(d, "ready.json"), "w", encoding="utf-8") as f:
        json.dump(marker, f)
    _say("Ready: %s (%d MB)" % (", ".join("%s %s" % kv for kv in vers.items()), marker["size_mb"]))


def _download(url, dest):
    """curl when there is one (it uses the system's certificates and proxy settings), else Python."""
    curl = shutil.which("curl")
    if curl:
        if _step([curl, "-fL", "--retry", "2", "-sS", "-o", dest, url], "download " + url.rsplit("/", 1)[-1]):
            raise RuntimeError("Couldn't download %s. Check your internet connection and try again." % url)
        return
    _say("$ download " + url.rsplit("/", 1)[-1])
    import urllib.request
    with urllib.request.urlopen(url, timeout=120) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)


def _install_spring(key):
    java, home, major = java_tools()
    if not java:
        raise RuntimeError(plan(key)["why"])
    m = _manifest(key)
    d = os.path.join(ENV_DIR, key)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    ver = m["maven"]
    tgz = os.path.join(d, "maven.tar.gz")
    _download("https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/%s/apache-maven-%s-bin.tar.gz" % (ver, ver), tgz)
    import tarfile
    with tarfile.open(tgz) as t:
        try:
            t.extractall(d, filter="data")
        except TypeError:            # Python < 3.12
            t.extractall(d)
    os.remove(tgz)
    os.replace(os.path.join(d, "apache-maven-%s" % ver), os.path.join(d, "maven"))
    warm = os.path.join(d, "warmup")
    shutil.copytree(os.path.join(ENV_SRC, key, "template"), warm)
    if _step([maven(key)] + maven_args(key) + ["test"], "mvn test  (Java %d; downloads Spring Boot and the test tools once)" % major,
             cwd=warm, env=spring_env(key)):
        raise RuntimeError("Maven couldn't download Spring Boot or build the check project (see Details).")
    boot = "?"
    try:
        import re
        with open(os.path.join(ENV_SRC, key, "template", "pom.xml"), encoding="utf-8") as f:
            boot = re.search(r"spring-boot-starter-parent</artifactId>\s*<version>([^<]+)", f.read()).group(1)
    except (OSError, AttributeError):
        pass
    shutil.rmtree(warm, ignore_errors=True)
    vers = {"Java": str(major), "Maven": ver, "Spring Boot": boot}
    marker = {"requirements": _req_hash(key), "versions": vers, "at": time.time(), "size_mb": _disk_mb(key)}
    with open(os.path.join(d, "ready.json"), "w", encoding="utf-8") as f:
        json.dump(marker, f)
    _say("Ready: %s (%d MB)" % (", ".join("%s %s" % kv for kv in vers.items()), marker["size_mb"]))


def _run(key):
    err = None
    try:
        {"django": _install_django, "node": _install_node, "spring": _install_spring}[key](key)
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
