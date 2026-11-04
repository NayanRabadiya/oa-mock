"""Compiles and runs submitted code with the compilers on this computer.

C++17 uses a real GCC when one is installed (Homebrew g++-NN on macOS) and falls back
to g++/clang++. Apple clang lacks <bits/stdc++.h>, so a shim header is provided.
Java uses javac/java from a JDK; Python uses the interpreter running this server.
"""
import glob, os, re, shutil, subprocess, sys, tempfile, time

IS_WIN = os.name == "nt"

def which(*names):
    for n in names:
        p = shutil.which(n)
        if p: return p
    return None

IS_MAC = sys.platform == "darwin"

# bits/stdc++.h for compilers that don't ship it (Apple clang on macOS)
SHIM_HEADERS = """#pragma once
#include <cassert>
#include <cctype>
#include <cfloat>
#include <climits>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <cstdint>
#include <algorithm>
#include <array>
#include <bitset>
#include <chrono>
#include <complex>
#include <deque>
#include <functional>
#include <iomanip>
#include <iostream>
#include <istream>
#include <iterator>
#include <limits>
#include <list>
#include <map>
#include <memory>
#include <numeric>
#include <optional>
#include <ostream>
#include <queue>
#include <random>
#include <set>
#include <sstream>
#include <stack>
#include <string>
#include <string_view>
#include <tuple>
#include <type_traits>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <variant>
#include <vector>
"""

def _version_key(path):
    m = re.search(r"(\d+)$", path)
    return int(m.group(1)) if m else 0

def find_cxx():
    """Prefer a real GCC (Homebrew g++-NN on macOS); fall back to g++/clang++."""
    cands = []
    for d in ("/opt/homebrew/bin", "/usr/local/bin", "/home/linuxbrew/.linuxbrew/bin"):
        cands += sorted(glob.glob(os.path.join(d, "g++-[0-9]*")), key=_version_key, reverse=True)
    for n in ["g++-%d" % v for v in range(16, 9, -1)] + ["g++", "clang++"]:
        p = shutil.which(n)
        if p: cands.append(p)
    for c in cands:
        try:
            v = subprocess.run([c, "--version"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=20).stdout.decode("utf-8", "replace")
        except Exception:
            continue
        return c, ("clang" in v.lower() or "apple" in v.lower()), v.splitlines()[0] if v else c
    return None, False, ""

GPP, GPP_IS_CLANG, GPP_DESC = find_cxx()   # resolved once at import
SHIM_DIR = None
if GPP and GPP_IS_CLANG:
    SHIM_DIR = os.path.join(tempfile.gettempdir(), "oamock_shim")
    os.makedirs(os.path.join(SHIM_DIR, "bits"), exist_ok=True)
    with open(os.path.join(SHIM_DIR, "bits", "stdc++.h"), "w") as f: f.write(SHIM_HEADERS)

def cxx_args(src, exe):
    a = [GPP, "-std=c++17", "-O2"]
    if SHIM_DIR: a += ["-I", SHIM_DIR]
    if IS_MAC: a += ["-Wl,-stack_size,0x10000000"]   # 256 MB stack for deep recursion
    return a + ["-o", exe, src]
JAVAC, JAVA = which("javac"), which("java")
PY = sys.executable

def run_cmd(args, inp, limit_s, cwd):
    t = time.perf_counter()
    try:
        p = subprocess.run(args, input=inp.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=limit_s, cwd=cwd)
        ms = (time.perf_counter() - t) * 1000
        out = p.stdout.decode("utf-8", "replace")
        err = p.stderr.decode("utf-8", "replace")
        if p.returncode != 0 and not err: err = "Process exited with code %d" % p.returncode
        elif p.returncode == 0: err = ""
        return {"out": out[:200000], "err": err[-4000:], "ms": ms, "tle": False}
    except subprocess.TimeoutExpired:
        return {"out": "", "err": "", "ms": limit_s * 1000, "tle": True}

def judge(lang, code, inputs, limit_ms):
    limit = max(0.5, min(limit_ms / 1000.0, 15))
    d = tempfile.mkdtemp(prefix="oamock_")
    try:
        if lang == "cpp":
            if not GPP: return {"compile_error": "No C++ compiler found. On macOS run: xcode-select --install  (or: brew install gcc). On Windows install MinGW-w64 and add g++ to PATH. Then restart this runner."}
            src = os.path.join(d, "main.cpp"); exe = os.path.join(d, "main.exe" if IS_WIN else "main")
            open(src, "w", encoding="utf-8").write(code)
            c = subprocess.run(cxx_args(src, exe), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90)
            if c.returncode != 0: return {"compile_error": c.stderr.decode("utf-8", "replace")[-6000:]}
            args = [exe]
        elif lang == "java":
            if not (JAVAC and JAVA): return {"compile_error": "javac/java were not found. Install a JDK and restart this runner."}
            open(os.path.join(d, "Main.java"), "w", encoding="utf-8").write(code)
            c = subprocess.run([JAVAC, "-encoding", "UTF-8", "Main.java"], cwd=d, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
            if c.returncode != 0: return {"compile_error": c.stderr.decode("utf-8", "replace")[-6000:]}
            args = [JAVA, "-Xss256m", "-cp", d, "Main"]
        elif lang == "py":
            open(os.path.join(d, "main.py"), "w", encoding="utf-8").write(code)
            args = [PY, "-X", "utf8", os.path.join(d, "main.py")]
        else:
            return {"compile_error": "Unsupported language: %s" % lang}
        return {"results": [run_cmd(args, i, limit, d) for i in inputs]}
    finally:
        shutil.rmtree(d, ignore_errors=True)



def describe():
    """One line per language, printed at start-up."""
    return [
        ("C++", (GPP_DESC + ("  [bits/stdc++.h provided by the runner]" if SHIM_DIR else "")) if GPP else "NOT FOUND (macOS: xcode-select --install or brew install gcc; Windows: run setup.bat)"),
        ("Java", JAVAC or "NOT FOUND (install a JDK, or run the setup script)"),
        ("Python", PY),
    ]

