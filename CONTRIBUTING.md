# Contributing

This is a group effort. If you sat an OA, or have a write-up or photos of one, add it so the next person can practise on it. Using an LLM to turn your notes into questions and tests is fine, as long as you check the result (step 4 below).

## How to add an OA

1. **Fork** this repo and create a branch, e.g. `add-google-oa-2026`.
2. **Transcribe the source** into `sources/<company>/` as Markdown, or JSON for structured parts such as an API spec. Put the original PDFs or photos in `raw-sources/` (git-ignored). Never commit them.
3. **Write the questions** in `data/<company>/`:
   - `company.json`: `key`, `name`, `tagline`, `blurb`, `headline`, `defaultFmt`, `formats` (with `pools` of question ids), `order`, `custom`, `offlist`. Copy `data/flipkart/company.json` as a template.
   - `questions/<id>.json`, one per question. Copy an existing one. A coding question needs `id`, `type: "code"`, `title`, `diff` (Easy/Medium/Hard), `src`, `body`, `inp`, `out`, `cons`, `samples` (each `{in, out, ex}`), `hidden` (each `{in, out}`), `ref` (Python) and ideally `refcpp`.
   - For LeetCode-style questions (the user fills in a function), add `stub` and `driver` per language, as in `data/amazon/questions/flip.json`.
4. **Check it:**
   ```
   python3 tools/check_refs.py <company>     # every reference must pass every test
   python3 run.py                            # open it and try the question yourself
   ```
   Make the hidden tests cover edge cases and at least one maximum-size input, so slow solutions fail.
5. **Open a pull request.** Say where the questions come from (company, role, college, date) and what you guessed where the source was incomplete.

## Rules

- Paraphrase statements in your own words. Don't paste the test platform's text wholesale.
- No personal data: no names, emails or roll numbers of candidates. Demo credentials shown inside a test are fine.
- If a statement is too incomplete to grade, add it to `offlist` in `company.json` with a short reason instead of guessing.
- Keep the server dependency-free (Python standard library only) and the frontend build-free.

## Prompt you can give an LLM

> Here are my notes/photos from the `<Company>` OA. Following the format of `data/amazon/questions/flip.json` in https://github.com/rgabhi/oa-mock, write one JSON file per question with a clear statement, 2 samples with explanations, 8–12 hidden tests (edge cases plus one large input), and reference solutions in Python and C++. Also write a Markdown transcription of the notes for `sources/<company>/`. List anything you had to assume.

Then run `tools/check_refs.py` before you open the PR. LLM-written tests are often wrong.
