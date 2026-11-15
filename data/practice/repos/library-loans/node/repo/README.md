# Library Loans API (Node.js)

## Overview
A small library lends books to its members. This API lists the books, lends them out and takes them back,
charging a fee when a book comes back late.

Two of the integrated tests fail. Find out why and fix the API so that they pass. This is a warm-up: a small
codebase with two bugs, to practise the read, run, trace and fix loop before the full repository tasks.

## API
| Request | Response |
|---|---|
| `GET /api/books` | every book with `available`, the copies on the shelf (`copies` minus open loans) |
| `POST /api/loans` `{"memberId", "bookId", "borrowedAt"}` | 201 with the loan `{"id", "memberId", "bookId", "borrowedAt", "returnedAt": null}` |
| `POST /api/loans/{loanId}/return` `{"returnedAt"}` | 200 `{"loanId", "returnedAt", "daysLate", "fee"}` |

Dates look like `2026-11-15` (today when left out). Errors come back as `{"message": ...}`:
400 "memberId and bookId are required" · "borrowedAt must be a date like 2026-11-15" · "returnedAt must be a date like 2026-11-15";
404 "Member not found" · "Book not found" · "Loan not found"; 409 "No copies available" · "Loan limit reached" · "Loan already returned".

## Lending rules
- A member can have at most **3** books out at once; a 4th loan is refused ("Loan limit reached").
- A book can be borrowed only while a copy is on the shelf ("No copies available").
- A book is due **14 days** after it was borrowed; one returned on day 14 is on time.
- The late fee is **10 per day** after the due date, at most **200** per loan.

## Getting started
```
npm install          # already done in this environment
npm test             # run the tests
npm start            # http://localhost:5000, with data/seed.json loaded
```

## Project structure
```
app.js, server.js
config/loanRules.js              the lending rules
data/store.js, data/seed.json    the in-memory store and the sample data
utils/dates.js                   calendar-day arithmetic
services/loanService.js          copies on the shelf, who may borrow
services/feeService.js           late fees
controllers/loanController.js    the API
routes/loanRoutes.js
tests/                           the integrated tests (read-only)
```

## Additional Information
- The data lives in an in-memory store standing in for the library database. The app loads `data/seed.json` when it
  starts; each test loads its own data.
- The code repository may intentionally contain other issues that are unrelated to this specific task.
  Please focus only on the described task requirements and address bugs or errors directly associated with them.
