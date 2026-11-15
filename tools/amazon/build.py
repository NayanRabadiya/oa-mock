"""Builds data/amazon/ (company.json + questions/*.json) from the sources in this folder.

    python3 tools/amazon/build.py

Needs Python 3.8+, node and g++ (the coding generator checks references against brute force)."""
import json, random, html, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(ROOT, 'data', 'amazon')
H = lambda *p: os.path.join(HERE, *p)
sys.path.insert(0, HERE)

# 1. regenerate the coding tests
subprocess.run([sys.executable, H('gen_coding.py')], check=True)

esc = html.escape
import fnstyle
coding = fnstyle.apply(json.load(open(H('build', 'coding_qs.json'))))
# ---- SJT: shuffle option order (seeded) so the best answer isn't always in the same slot
random.seed(7)
items = json.load(open(H('sjt.json')))
for it in items:
    random.shuffle(it["o"])
sjt = {
    "id": "sjt", "type": "sjt", "title": "Workplace Situational Judgement", "diff": "SJT",
    "src": "Amazon SDE Intern OA 2026 · section 3 (scenarios written for this mock)",
    "body": "<p>For each scenario, pick the response you would most likely take. The real section covers teamwork and communication, ownership and customer focus, handling disagreement, taking feedback and decision making, and it maps onto Amazon's Leadership Principles.</p><p class=\"muted\">The real OA's scenarios weren't shared, so these are original ones in the same style. Scoring: 2 points for the best answer, 1 for a partly good one, 0 otherwise.</p>",
    "items": items, "inp": "", "out": "", "cons": [], "samples": [], "hidden": [], "ref": "",
    "lc": None, "lcurl": None,
}

# ---- repository version of the debugging task: real projects in data/amazon/repos/watchlist-repo/<stack>/
watchlist_repo = {
    "id": "watchlist-repo", "type": "repo", "title": "MovieDB Watchlist (repository)", "diff": "Repo",
    "src": "Amazon SDE Intern OA 2026 · section 2, AI-assisted repository task",
    "body": open(H('watchlist_repo.html')).read().strip(),
    "stacks": ["node", "django", "spring"],
    "inp": "", "out": "", "cons": [], "samples": [], "hidden": [], "ref": "", "lc": None, "lcurl": None,
}

QS = coding + [watchlist_repo, sjt]
CFG = {
    "key": "amz", "name": "Amazon OA Mock",
    "tagline": "SDE Intern 2026: coding · repo debugging · situational judgement",
    "headline": "Sit a timed Amazon OA, then see what passed.",
    "blurb": "questions reported from Amazon's 2026 SDE intern OAs: coding, a repo-debugging task and situational judgement",
    "defaultFmt": "sde",
    "ioRule": "Coding questions are LeetCode-style: complete the given function and return the answer. Input and output are handled for you, so don't print anything yourself: extra output counts as a wrong answer.", "custom": ["flip", "findpairs", "parcels", "outlier", "winners", "qmarks", "watchlist-repo", "sjt"],
    "formats": {
        "sde": {"name": "SDE Intern OA 2026", "desc": "3 sections: coding (Longest Run After One Flip), the MovieDB repository task (Node.js, Django or Spring Boot), situational judgement · 120 min", "mins": 120, "pools": [["flip"], ["watchlist-repo"], ["sjt"]]},
        "coding": {"name": "IIITD coding set", "desc": "Palindrome-Ready Subsequences + Even Blocks of At Most Two (IIIT Delhi, 4 July) · 70 min", "mins": 70, "pools": [["palsub"], ["evenrun"]]},
        "online2024": {"name": "Online coding set 2024", "desc": "Five coding questions reported from Amazon's 2024 online OAs (HackerRank) · 150 min", "mins": 150, "pools": [["findpairs"], ["parcels"], ["outlier"], ["winners"], ["qmarks"]]},
        "repo": {"name": "Repository task", "desc": "MovieDB watchlist as a real project: pick your environment, then fix the backend until the tests pass · 60 min", "mins": 60, "pools": [["watchlist-repo"]]},
        "custom": {"name": "Custom", "desc": "Pick the questions and the time", "mins": 60, "pools": []},
    },
    "offlist": [
        {"t": "Return/Risk Evaluation System (repo debugging)", "s": "Amazon SDE-1 Intern OA 2026 · section 2",
         "why": "Only an outline was shared (7+ files, return-window checks, linked accounts, risk scoring, approve/review/reject decisions, 6 integrated tests). It is coming as a repository question, reconstructed from the outline. Until then the MovieDB repository task practises the same read-trace-fix workflow."},
    ],
}


# 2. write data/amazon/
CFG["order"] = [q["id"] for q in QS]
os.makedirs(os.path.join(OUT, "questions"), exist_ok=True)
json.dump(CFG, open(os.path.join(OUT, "company.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
META_KEYS = ("year", "month", "college", "role", "alsoSeen")   # kept from the existing file, so a rebuild doesn't drop them
for q in QS:
    p = os.path.join(OUT, "questions", q["id"] + ".json")
    if os.path.isfile(p):
        old = json.load(open(p, encoding="utf-8"))
        for k in META_KEYS:
            if k in old and k not in q: q[k] = old[k]
    json.dump(q, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("wrote", OUT, [q["id"] for q in QS])
