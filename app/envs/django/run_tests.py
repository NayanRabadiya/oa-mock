"""Runs a Django project's tests the way `python manage.py test` does and also writes a JUnit XML report.

    python run_tests.py <project folder> <report.xml> [test labels...]

Used by the OA Mock app (app/server/repos.py) so it can show a result per test, like HackerRank's
JUnit-based scoring. Standard library only, besides Django itself.
"""
import os
import re
import sys
import time
import traceback
import unittest
import xml.etree.ElementTree as ET


def main():
    project, report = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    labels = sys.argv[3:]
    os.chdir(project)
    sys.path.insert(0, project)
    try:
        with open("manage.py", encoding="utf-8") as f:
            m = re.search(r"DJANGO_SETTINGS_MODULE['\"]\s*,\s*['\"]([\w.]+)", f.read())
    except OSError:
        m = None
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", m.group(1) if m else "settings")

    records = []

    class Result(unittest.TextTestResult):
        def startTest(self, test):
            self._t0 = time.time()
            super().startTest(test)

        def _add(self, test, status, err=None):
            msg = ""
            if err is not None:
                msg = "".join(traceback.format_exception(*err)) if isinstance(err, tuple) else str(err)
            records.append({"id": test.id(), "status": status, "time": time.time() - getattr(self, "_t0", time.time()),
                            "message": msg})

        def addSuccess(self, test):
            super().addSuccess(test); self._add(test, "passed")

        def addFailure(self, test, err):
            super().addFailure(test, err); self._add(test, "failed", err)

        def addError(self, test, err):
            super().addError(test, err); self._add(test, "error", err)

        def addSkip(self, test, reason):
            super().addSkip(test, reason); self._add(test, "skipped", reason)

        def addExpectedFailure(self, test, err):
            super().addExpectedFailure(test, err); self._add(test, "passed")

        def addUnexpectedSuccess(self, test):
            super().addUnexpectedSuccess(test); self._add(test, "failed", "unexpected success")

        def addSubTest(self, test, subtest, err):
            super().addSubTest(test, subtest, err)
            if err is not None:
                self._add(test, "failed" if issubclass(err[0], test.failureException) else "error", err)

    import django
    from django.test.runner import DiscoverRunner

    class Runner(DiscoverRunner):
        def get_resultclass(self):
            return Result

    code = 1
    try:
        django.setup()
        failures = Runner(verbosity=2, interactive=False).run_tests(labels)
        code = 1 if failures else 0
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else 1
    except Exception:
        traceback.print_exc()
        records.append({"id": "setup", "status": "error", "time": 0, "message": traceback.format_exc()})
    write_report(report, records)
    return code


def write_report(path, records):
    # a test with a failing subTest and a final success is reported once, as failed
    merged = {}
    for r in records:
        prev = merged.get(r["id"])
        if prev is None or prev["status"] == "passed":
            merged[r["id"]] = r
    suite = ET.Element("testsuite", name="django", tests=str(len(merged)),
                       failures=str(sum(r["status"] == "failed" for r in merged.values())),
                       errors=str(sum(r["status"] == "error" for r in merged.values())))
    for r in merged.values():
        cls, _, name = r["id"].rpartition(".")
        case = ET.SubElement(suite, "testcase", classname=cls, name=name, time="%.3f" % r["time"])
        if r["status"] in ("failed", "error", "skipped"):
            tag = {"failed": "failure", "error": "error", "skipped": "skipped"}[r["status"]]
            el = ET.SubElement(case, tag, message=(r["message"].strip().splitlines() or [""])[-1][:500])
            el.text = r["message"]
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    ET.ElementTree(suite).write(path, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    sys.exit(main())
