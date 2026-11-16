# Wallet API (Node.js)

## Overview
A payments team runs customer wallets with this API: money is deposited, withdrawn and transferred between
wallets, and every change is recorded in the wallet's transaction history. Balances are whole rupees.

Several integrated tests fail. Find out why and fix the API so that every test passes.

## API
| Request | Response |
|---|---|
| `GET /api/wallets/{id}` | the wallet: `{"id", "owner", "balance", "status"}` |
| `POST /api/wallets/{id}/deposit` `{"amount", "at"}` | 200 `{"wallet", "transaction"}` |
| `POST /api/wallets/{id}/withdraw` `{"amount", "at"}` | 200 `{"wallet", "transaction"}` |
| `POST /api/transfers` `{"from", "to", "amount", "at"}` | 201 `{"from": wallet, "to": wallet, "amount"}` |
| `GET /api/wallets/{id}/transactions?type=&limit=` | the wallet's transactions, newest first |

A transaction is `{"id", "walletId", "type", "amount", "balanceAfter", "counterparty", "at"}`. Its `type` is
`deposit`, `withdrawal`, `transfer_in` or `transfer_out`; `counterparty` is the other wallet of a transfer, else null.
Times look like `2026-11-15T09:30:00Z` (now when left out).

Errors come back as `{"message": ...}`:
400 "amount must be a positive whole number" · "from, to and amount are required" · "Cannot transfer to the same wallet" ·
"Invalid transaction type" · "limit must be between 1 and 100" · a bad time;
404 "Wallet not found"; 409 "Insufficient funds" · "Wallet is frozen".

## Rules
- Amounts are positive whole numbers (JSON numbers, not strings).
- A wallet can't go below 0. A frozen wallet can't deposit, withdraw, send or receive.
- A transfer is all or nothing: if anything is wrong (a missing or frozen wallet, not enough money), no balance
  changes and no transaction is recorded.
- The history is newest first (the later transaction first when the times are equal). `type` filters it;
  `limit` (1 to 100, default 20) caps it.

## Getting started
```
npm install          # already done in this environment
npm test             # run the tests
npm start            # http://localhost:5000, with data/seed.json loaded
```

## Project structure
```
app.js, server.js
config/limits.js                   page sizes, transaction types
data/store.js, data/seed.json      the in-memory store and the sample data
utils/time.js                      ISO times
services/walletErrors.js           errors with their HTTP status
services/walletService.js          deposits, withdrawals, history
services/transferService.js        transfers between wallets
controllers/walletController.js    the API
routes/walletRoutes.js             paths
tests/                             the integrated tests (read-only)
```

## Additional Information
- The data lives in an in-memory store standing in for the wallet database. The app loads `data/seed.json` when it starts;
  each test loads its own data.
- The code repository may intentionally contain other issues that are unrelated to this specific task.
  Please focus only on the described task requirements and address bugs or errors directly associated with them.
