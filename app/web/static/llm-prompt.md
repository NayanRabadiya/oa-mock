You are helping add a question to OA Mock (https://github.com/rgabhi/oa-mock), a practice platform for online assessments. I'll give you my notes, photos or memory of a question from a real OA. Write ONE JSON object for it, in this exact format, and nothing else:

```json
{
  "id": "pairsum",
  "type": "code",
  "title": "Pairs With Sum K",
  "diff": "Easy",
  "src": "Company OA 2026 (SDE intern, on-campus)",
  "year": 2026,
  "month": 8,
  "college": "IIT Delhi",
  "role": "SDE Intern",
  "body": "<p>Statement in your own words, as HTML (<p>, <code>, <ul>, <b>).</p>",
  "inp": "First line: n and k. Second line: n integers a[1..n].",
  "out": "The number of pairs.",
  "cons": "1 ≤ n ≤ 2·10^5, |a[i]| ≤ 10^9",
  "samples": [
    {"in": "4 5\n1 4 2 3\n", "out": "2", "ex": "Pairs (1,4) and (2,3)."}
  ],
  "hidden": [
    {"in": "3 4\n2 2 1\n", "out": "1"}
  ],
  "spec": {
    "fn": "countPairs",
    "read": [["_n", "int"], ["k", "int"], ["nums", "int[]", "_n"]],
    "ret": "long",
    "returns": "the number of pairs"
  },
  "ref": "class Solution:\n    def countPairs(self, k: int, nums: List[int]) -> int:\n        c = Counter(); r = 0\n        for x in nums:\n            r += c[k - x]; c[x] += 1\n        return r\n",
  "refcpp": "class Solution {\npublic:\n    long long countPairs(int k, vector<int>& nums) { ... }\n};\n",
  "wrong": [
    {"why": "brute force O(n^2)", "ref": "class Solution:\n    def countPairs(self, k, nums): ..."},
    {"why": "counts a pair of an element with itself", "ref": "class Solution:\n    def countPairs(self, k, nums): ..."}
  ]
}
```

Rules:
- `id`: short, lowercase, no spaces. `diff`: Easy, Medium or Hard. Add `year`, `month`, `college`, `role` only if my notes say them. Never guess them.
- The statement is in your own words. No candidate names, emails or roll numbers.
- Tests are plain stdin text and the exact expected stdout. `samples`: 1-2 with an explanation in `ex`. `hidden`: 8-15 tests covering edge cases (smallest n, duplicates, negatives, all equal, answer 0, overflow) and at least one maximum-size input. Hidden tests must not all have the same answer.
- Compute every expected output by running the reference solution. Don't work outputs out by hand.
- `spec` says how the hidden driver reads the input and calls the function (LeetCode style). `read` items, in input order:
  - `[name, "int"|"long"|"double"|"str"]` reads one token.
  - `[name, "int[]"|"long[]"|"double[]"|"str[]", L]` reads L tokens. L is a number or the name of an earlier item.
  - `[name, "int[][]", R, C]` reads R rows of C ints.
  - `[name, "line"]` reads the whole input as one string.
  - `["rows", L, [[name, type], ...]]` reads L rows of mixed columns, one array per column.
  - Names starting with `_` are read but not passed to the function (counts the arrays already carry).
  - Use `long` for values that can exceed 2^31.
  - `ret` is one of `int`, `long`, `str`, `bool`, `int[]`, `long[]`, `str[]` (printed on one line), `int[]/lines`, `long[]/lines`, `str[]/lines`, `bool[]/lines` (one value per line) or `int[][]` (one row per line).
  - Decimals: read them as `double` / `double[]` (also as `rows` columns). A `double`, `double[]` or `double[]/lines` result needs `"dp": <decimals>` in the spec, and the driver prints it with exactly that many digits after the point (like `%.4f`). Keep every expected answer clearly away from a rounding tie, so all four languages print the same text.
- `ref`: Python 3, `class Solution` with the function named in `spec.fn`. Its parameters are the `read` names without `_`, in order. `List`, `Counter`, `defaultdict`, `heapq`, `bisect`, `math` and so on are already imported. It must be fast enough for the maximum input (about 1-2 s).
- `refcpp` (optional): C++17 `class Solution` with the same function.
- `wrong`: 1-2 plausible wrong solutions in the same shape as `ref`, such as brute force that is too slow, an off-by-one, or a missed edge case. The checks make sure the hidden tests catch them.

If it isn't a coding question, use one of these formats instead (same rules for `id`, `src`, `year`, `month`, `college`, `role`, `body`, and for computing every expected output by running the reference, never by hand):

**SQL** (`"type": "sql"`, `"diff": "SQL"`). Answers run in AlaSQL in the browser; rows are compared as a set, numbers to 3 decimals.
```json
{
  "id": "deptavg", "type": "sql", "diff": "SQL", "title": "...", "body": "<p>...which columns to return, in which order...</p>",
  "inp": "The tables below. Each test runs your query on a different set of rows.",
  "out": "The rows of your query, compared as a set.",
  "cons": ["Name matches are case-sensitive"],
  "schema": [{"t": "employees", "cols": [["employee_id", "INT"], ["name", "STRING"], ["salary", "INT"]]}],
  "samples": [{"tables": {"employees": {"cols": ["employee_id", "name", "salary"], "rows": [[1, "Asha", 90000]]}},
               "out": [["Asha", 90000]], "ex": "Why this is the answer."}],
  "hidden": [ ...8-15 tests in the same shape, including ones whose answer is empty and ones that catch each trap... ],
  "ref": "SELECT name, salary FROM employees WHERE ...;",
  "wrong": [{"why": "forgets the second filter", "ref": "SELECT ..."}]
}
```
Every test has every table in `schema`, with the same columns in the same order.

**Debugging** (`"type": "debug"`, `"diff": "Debug"`). The page runs `pre` + the solver's files + `post` as one JavaScript program, like Node: `console.log` is the output, `require("fs").readFileSync(0)` returns the test's input, top-level `await` works if you wrap it in `return (async () => { ... })()`, and each test gets 4 seconds. Output lines starting with `[log]` are shown but not graded.
- `starter`: the editable files with the bugs, `ref`: the same files fixed. Mark each file with a comment line such as `// ---- file: controllers/cart.js ----`.
- `pre`: read-only code before them (stand-ins for the framework, models, helpers). `post`: read-only code after them (the app wiring and a test client that reads the input and prints one line per request). Use `""` if there is none.
- `samples` / `hidden`: `{"in": "...", "out": "..."}` like a coding question, with `out` produced by running `ref`. The starter must fail some of them.
- `bugs`: every bug, in order of where it is in the files, as the edits that put it back into `ref`: `{"why": "removeItem never deletes", "edits": [{"fixed": "exact text in ref", "buggy": "what starter has instead"}]}`. Each `fixed` text must appear exactly once in `ref`. The checks put each bug back on its own and make sure a test fails, and check that putting all of them back gives `starter`.
- `fixnotes`: HTML list of what was broken and how to fix it (shown in the report).

**Situational judgement** (`"type": "sjt"`, `"diff": "SJT"`).
```json
{
  "id": "sjt", "type": "sjt", "diff": "SJT", "title": "Workplace Situational Judgement", "body": "<p>For each scenario, pick the response you would most likely take...</p>",
  "items": [
    {"lp": "Ownership", "s": "The scenario.", "o": [["An option.", 0], ["A partly good option.", 1], ["The best option.", 2], ["Another weak option.", 0]],
     "why": "Why the best option is best."}
  ]
}
```
8-15 scenarios with 3-6 options each. Scores: 2 for the single best option, 1 for partly good, 0 for weak. Vary where the best option is. `lp` is the principle or skill the scenario tests.

After the JSON, list anything you had to assume because my notes were incomplete.

My notes:
