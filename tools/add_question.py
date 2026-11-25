#!/usr/bin/env python3
"""Checks a question and adds it to the bank: the same checks as the app's "Add a question" page and the
pull-request check.

    python3 tools/add_question.py <company> new.json           # check only
    python3 tools/add_question.py <company> new.json --save    # check, then write data/<company>/questions/<id>.json
                                                              #   (+ company.json for a new company, --name "Google";
                                                              #    --replace to overwrite a question with the same id)
    python3 tools/add_question.py --check data/<company>/questions/<id>.json [...]   # re-check questions in the bank
    python3 tools/add_question.py --changed origin/main       # every question changed since a git ref (used by CI)

Checks, by "type" (see app/server/contribute.py):
  coding (default)  format; the function "spec" (generates the LeetCode stub and the hidden input/output driver in
                    Python, C++, Java and JavaScript); the references pass every test; the 4 drivers read every input
                    the same way; tests catch the known-wrong solutions in "wrong"
  sql               format and tables match "schema"; the reference query gives the expected rows on every test in
                    AlaSQL (the page's engine); the known-wrong queries in "wrong" fail a test
  debug             the fixed files ("ref") pass every test; the buggy files ("starter") fail one; each bug in "bugs",
                    put back into the fixed files on its own, fails a test
  sjt               every scenario has 3-6 options, each scored 0/1/2, exactly one best answer, and a reason
  repo              per stack: the repository with the fixes in solution/ passes every test (hidden ones too), the
                    starting repository fails a visible test, and each bug in repo.json, on its own, fails a test.
                    Needs that stack's environment (python3 tools/setup_env.py django)
and for every type: not already in the bank. SQL and debugging need Node.js (node). Exit code 1 if any check fails.
"""
import json, os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "app"))
from server import contribute  # noqa: E402

MARK = {"ok": "\033[32m ok \033[0m", "warn": "\033[33mwarn\033[0m", "fail": "\033[31mFAIL\033[0m", "skip": "skip"}


def report(title, res):
    print("\n== %s" % title)
    for c in res["checks"]:
        lines = (c["detail"] or "").splitlines() or [""]
        print(" [%s] %-26s %s" % (MARK[c["status"]], c["name"], lines[0]))
        for l in lines[1:12]:
            print("        %-26s %s" % ("", l))
    return res["ok"]


def from_bank(path):
    path = os.path.abspath(path)
    company = os.path.basename(os.path.dirname(os.path.dirname(path)))
    with open(path, encoding="utf-8") as f:
        return company, json.load(f)


def changed(ref):
    out = subprocess.run(["git", "-C", ROOT, "diff", "--name-only", "--diff-filter=AM", ref, "--", "data/"],
                         stdout=subprocess.PIPE, check=True).stdout.decode().split()
    paths = [os.path.join(ROOT, p) for p in out if p.count("/") == 3 and "/questions/" in p and p.endswith(".json")]
    for p in out:                       # a change inside data/<company>/repos/<qid>/ re-checks that question
        bits = p.split("/")
        if len(bits) > 4 and bits[2] == "repos":
            q = os.path.join(ROOT, "data", bits[1], "questions", bits[3] + ".json")
            if os.path.isfile(q) and q not in paths:
                paths.append(q)
    return paths


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__); return 0
    ok = True
    if argv[0] in ("--check", "--changed"):
        paths = changed(argv[1] if len(argv) > 1 else "origin/main") if argv[0] == "--changed" else argv[1:]
        if not paths:
            print("no question files to check"); return 0
        for p in paths:
            company, q = from_bank(p)
            ok &= report("%s/%s" % (company, q.get("id")), contribute.check(company, q, replace=True))
        return 0 if ok else 1
    company, path = argv[0], argv[1]
    with open(path, encoding="utf-8") as f:
        q = json.load(f)
    replace = "--replace" in argv
    ok = report("%s/%s" % (company, q.get("id")), contribute.check(company, q, replace=replace))
    if ok and "--save" in argv:
        name = argv[argv.index("--name") + 1] if "--name" in argv else None
        for p in contribute.save(company, q, name=name, replace=replace):
            print("wrote", p)
    elif not ok:
        print("\nFix the failing checks and run this again.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
