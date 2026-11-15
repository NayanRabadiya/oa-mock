#!/usr/bin/env python3
"""Sets up an environment for repository questions from a terminal (the app's environment menu does the same).

    python3 tools/setup_env.py django          # set it up (prints the log); exit 1 if it fails
    python3 tools/setup_env.py --status        # what's set up
"""
import json, os, sys, time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "app"))
from server import envs  # noqa: E402


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__); return 0
    if argv[0] == "--status":
        for k, e in envs.status()["envs"].items():
            print("%-8s %-9s %s" % (k, e["state"], json.dumps(e.get("installed") or e.get("plan"))))
        return 0
    key = argv[0]
    if envs.ready(key):
        print("%s is already set up" % key); return 0
    envs.start("install", key)
    shown = 0
    while True:
        j = envs.job()
        log = j.get("log", "")
        if len(log) > shown:
            sys.stdout.write(log[shown:]); sys.stdout.flush(); shown = len(log)
        if j.get("state") != "running":
            break
        time.sleep(0.5)
    if j.get("state") != "done":
        print("failed: %s" % j.get("error")); return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
