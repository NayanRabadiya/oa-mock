# OA Mock

**Practice online assessments for Flipkart, Juspay and Amazon on your own computer.** The tests use questions reported from real OAs, with hidden test cases, HackerRank-style partial marks and a scorecard at the end. You can sit a test timed or untimed.

![Amazon OA Mock home](docs/home.png)

- **Real formats:** each company's test layout is reproduced (for example, Amazon's 3-section SDE Intern OA), or you can build a custom set.
- **Your languages:** C++17, Java, Python 3 and JavaScript compile and run natively on your machine.
- **Graded like the real thing:** Run checks the samples, and Submit runs every hidden test. Score = tests passed / total × 100, and your best submission counts.
- **Timed or not:** a countdown that auto-submits, or **No timer** with a count-up clock.
- **Learn afterwards:** the report shows your code, reference solutions (Python + C++) and a LeetCode question with the same pattern.
- **Private:** no account, no camera, no proctoring. The runner only listens on `127.0.0.1`, and history is saved in your browser.

---

## Quick start

```
git clone https://github.com/rgabhi/oa-mock.git
cd oa-mock
```

| OS | First time | After that |
|---|---|---|
| **Windows 10/11** | double-click **`setup.bat`** | double-click **`start.bat`** |
| **macOS** | `./setup.sh` | `./start.sh` |
| **Linux** | `./setup.sh` | `./start.sh` |

The setup script installs whatever is missing, then opens **http://127.0.0.1:8765** in your browser.

| Tool | Needed for | Windows | macOS | Linux |
|---|---|---|---|---|
| Python 3.8+ | the mock itself (**required**) | `winget` Python 3.12 | python.org / Homebrew | package manager |
| C++ compiler | C++ answers | MinGW-w64 (WinLibs) via `winget` | Apple Command Line Tools* | `g++` |
| Java JDK | Java answers | Temurin 21 via `winget` | `brew install openjdk` | OpenJDK |

\*Apple clang works: the runner supplies `<bits/stdc++.h>` itself.

Linux setup supports apt, dnf, yum, pacman, zypper and apk (with `sudo`). Options:

```
./setup.sh --no-java      # skip the JDK
./setup.sh --no-start     # set up only, don't launch
setup.bat -NoJava -NoStart
```

**No scripts?** If you have Python, just run `python3 run.py` (`py run.py` on Windows). Options: `--port 9000`, `--no-browser`. You can also set `OA_PORT`.

---

## How a test works

1. **Pick a company and a format**, or press **Practise** on any question in the bank.
2. Set the **minutes**, or tick **No timer**.
3. **Run code** (`Ctrl+Enter`) checks the sample cases. **Submit code** (`Ctrl+Shift+Enter`) runs all hidden tests. Read from STDIN and write to STDOUT, as on HackerRank.
4. **Move between questions** with **◀ Prev / Next ▶**, the Q1, Q2… tabs or `Alt+←/→`. In Practice, a dropdown takes you to any question in the bank, and your code is kept as you move.
5. **⌂ Home** takes you back to the company page without ending anything. A banner there lets you **Resume**. In a timed test the clock keeps running.
6. **End test** (or let the timer run out) to see the report. From the report you can go back to the company home, start again, or open **All companies**. Tab switches are counted, like a proctored test.

![Coding question](docs/coding.png)

| Report | Situational judgement |
|---|---|
| ![Report](docs/report.png) | ![SJT](docs/sjt.png) |

---

## Question banks

### Amazon

| Section | Question | Source |
|---|---|---|
| Coding | Longest Run After One Flip (Easy) | SDE-1 Intern OA 2026 |
| Coding | Palindrome-Ready Subsequences (Medium) | 2026 Intern OA, IIIT Delhi, 4 July |
| Coding | Even Blocks of At Most Two (Hard) | 2026 Intern OA, IIIT Delhi, 4 July |
| Repo debugging | **MovieDB Watchlist (MERN)** | SDE Intern OA 2026, section 2 |
| Situational judgement | 12 workplace scenarios | Section 3 (scenarios written for this mock) |

Amazon's coding questions are **LeetCode-style**. You complete `class Solution` (or a function in JavaScript) in any of the four languages and return the answer. A hidden driver reads the input and prints your result, so Run, Submit and Custom input work as usual.

**Formats:** SDE Intern OA 2026 (all 3 sections, 120 min) · IIITD coding set (70 min) · Debugging section (60 min) · Custom.

The **repo-debugging** question recreates the real task. You get the watchlist controller, rate limiter and routes with the bugs reported from the OA: the list never shows added movies, removal doesn't delete, the status check returns the wrong type, and the "10 operations per 2 minutes" rate limiter is broken and not wired in. It runs against an in-memory Express/Mongo stand-in with 10 integration tests. Server logs appear as `[log]` lines.

![Repo debugging question](docs/debugging.png)

The *Return/Risk Evaluation* repo task is listed but can't be run, because only an outline of it was reported.

### Flipkart

13 coding questions + 1 SQL (run on an in-browser SQL engine). Formats: **SDE**, **Data Engineer**, **UI Engineer**, Custom.

### Juspay

20 coding questions from HackerEarth, Rookies World, the Unstop hiring challenge and live elimination rounds. Formats: **Converging Maze**, **HackerEarth graph set**, **Unstop challenge**, **Elimination round**, Custom.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `OSError: Address already in use` | An older runner is still running, often because **Ctrl+Z** paused it instead of stopping it. Run `kill %1` or `lsof -ti tcp:8765 \| xargs kill`. The runner also falls back to the next free port. Always stop it with **Ctrl+C**. |
| "No C++ compiler found" | Run setup again. On Windows, open a **new** terminal after installing so `g++` is on your PATH. On macOS, finish the Command Line Tools installer and re-run `./setup.sh`. |
| Java not detected on macOS | `brew install openjdk`, then run the `sudo ln -sfn …` command that brew prints. |
| Blank page or "not found" | Open the mock through the server (`python3 run.py`), at the `127.0.0.1` address it prints. Opening the HTML files directly won't work. |

---

## How it's built

A small web app with a Python standard-library backend. There's nothing to `pip install` or `npm install`.

```
run.py                     entry point (python3 run.py [--port N] [--no-browser])
oa_mock/                   backend (Python 3.8+, stdlib only)
  __main__.py              start-up: prints compilers, binds 127.0.0.1, opens the browser
  server.py                HTTP routes: pages, static files, /api/companies, POST /run
  judge.py                 compiles and runs code: g++/clang (C++17), javac/java, Python
  data.py                  loads data/<company>/, reloading when files change
web/                       frontend (plain HTML/CSS/JS, no build step)
  index.html, app.html     company picker; the test app (one template for every company)
  static/css/              app.css, index.css
  static/js/core/          config.js (data, languages, saved state), util.js
  static/js/run/           workers.js (JavaScript answers in a Web Worker), sql.js, judge.js (calls /run, grades)
  static/js/exam/          session.js (start/end, editor), panels.js, controls.js (timer, navigation, Run/Submit)
  static/js/views/         render.js, home.js, exam.js, report.js
  static/js/main.js        global listeners and first render (loaded last)
  static/vendor/           CodeMirror 5 and AlaSQL, both MIT
data/<company>/            question banks
  company.json             name, test formats, question order, unrunnable entries
  questions/<id>.json      statement, samples, hidden tests, reference solutions, stubs/drivers
sources/                   text/JSON transcriptions of the source material (no PDFs or photos)
tools/
  check_refs.py            runs every reference solution against its tests
  amazon/                  generators that build data/amazon/ (statements, tests, debugging repo, SJT)
setup.sh, setup.ps1/.bat   one-shot installers; start.sh / start.bat launch
```

**Request flow.** `GET /amazon` renders `web/app.html`, which loads the vendored editor, then `/api/companies/amazon/data.js` (that company's config and questions), then the app scripts. C++, Java and Python answers are sent to `POST /run`. The server compiles and runs them and returns stdout, stderr and timings, and the page grades them against the tests. JavaScript answers and the debugging repo run in a Web Worker in the page. The server only listens on `127.0.0.1`, checks the `Host` header, and requires a per-run token on `/run`.

### Adding or editing questions

- **Edit:** change `data/<company>/questions/<id>.json` and reload the page. The server picks up changed files automatically.
- **Add a question:** create `questions/<id>.json` (copy an existing one as a template) and add the id to `order` in `company.json`. Mention it in a format's `pools` to include it in a test.
- **Add a company:** create `data/<key>/company.json` and `data/<key>/questions/`. It appears on the home page automatically.
- **Check:** run `python3 tools/check_refs.py [company]`. Every Python and C++ reference must pass its tests.
- **Amazon** is generated: edit the files in `tools/amazon/`, then run `python3 tools/amazon/build.py` (needs `node` and `g++`).
- **Sources:** keep original PDFs and photos in `raw-sources/` (git-ignored), and commit only text/JSON transcriptions under `sources/`.

The questions are paraphrased from candidates' reports and are for personal practice only.
