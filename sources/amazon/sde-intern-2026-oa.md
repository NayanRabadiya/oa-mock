# Amazon SDE-1 Intern Online Assessment (2026 batch)

Transcribed from a 2-page candidate write-up (`Amazon SDE 2026 OA.pdf`, not kept in this repo).

- **Role:** Software Development Engineer Intern
- **Year:** 2026 batch
- **Format:** 3 sections · difficulty medium–hard · focus: strings, debugging, behavioural

---

## Section 1: Coding

### 1. Maximum Consecutive 1s (Binary String)

**Problem.** Given a binary string `log` and an integer `k`, choose exactly one substring of length `k` and change every `0` inside it to `1`. Find the maximum number of consecutive `1`s possible after this operation.

**Example.**

```
log = "11001", k = 2
Selected window: 11[00]1 -> 11[11]1
Output: 5
```

**O(n) approach (from the write-up).** Flipping any window of length `k` contributes exactly `k` consecutive 1s, so for a window `[i, i+k-1]` the answer is:

```
(1s immediately before the window) + k + (1s immediately after the window)
```

Precompute in O(n):

- `left[i]`: consecutive 1s ending at index `i`
- `right[i]`: consecutive 1s starting at index `i`

Each window is then `left[i-1] + k + right[i+k]` (with boundary checks), evaluated in O(1).
Complexity: time O(n), space O(n).

→ Mock question: `data/amazon/questions/flip.json` (*Longest Run After One Flip*).

---

## Section 2: Repository Debugging & Simulation

### 2. Return/Risk Evaluation System (repository-based)

Unlike a standard DSA problem, this question gives you an existing repository of 7+ files, some 400–500+ lines long. The task is to understand and debug a return/risk evaluation system.

**System logic includes:**

- category returnability and return-window validation
- linked-account aggregation and return history
- order-value-based scoring and risk-score calculation
- auto-approve / manual-review / reject decisions and reason mapping

**Workflow the section rewards:** understand the codebase → understand the existing logic → run the tests → find why the tests fail → identify the right component → change the implementation → run the tests again → debug systematically.

It tests reading code, tracing execution and finding your way around an unfamiliar architecture until **6 integrated test cases** pass.

→ Not runnable in the mock, because only this outline was shared. Listed under *Not runnable* in the Amazon question bank. The MovieDB watchlist task (`moviedb-watchlist.md`) is the runnable debugging question.

---

## Section 3: Situational Judgement

### 3. Workplace Situational Judgement

A behavioural section on how a candidate works within an engineering team. The questions are practical workplace situations rather than a traditional exam.

**Focus areas:**

- teamwork and communication
- ownership and customer focus
- handling disagreements and taking feedback
- decision making

**Takeaway (from the write-up):** this section directly assesses Amazon's Leadership Principles. Overall, the OA tests a combination of data structures and algorithms, problem solving, understanding a codebase, debugging, testing and workplace decision making.

→ The real scenarios weren't shared. The mock's 12 scenarios (`tools/amazon/sjt.json`) are original.
