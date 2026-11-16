# Library Loans API (Spring Boot)

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
mvn test               # run the tests (the dependencies are already downloaded in this environment)
mvn spring-boot:run    # http://localhost:5000, with src/main/resources/seed.json loaded
```

## Project structure
```
src/main/java/com/library/
  LibraryApplication.java
  config/LoanRules.java              the lending rules
  store/LibraryStore.java, seed/     the in-memory store; seed.json is loaded at start-up
  model/                             books, members, loans
  util/Dates.java                    calendar-day arithmetic
  service/LoanService.java           copies on the shelf, who may borrow
  service/FeeService.java            late fees
  controller/LoanController.java     the API
src/test/java/com/library/           the integrated tests (read-only)
```

## Additional Information
- The data lives in an in-memory store standing in for the library database. The app loads `src/main/resources/seed.json` when it
  starts; each test loads its own data.
- The code repository may intentionally contain other issues that are unrelated to this specific task.
  Please focus only on the described task requirements and address bugs or errors directly associated with them.
