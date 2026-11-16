# Return / Risk Evaluation Service (Node.js / Express)

## Overview
When a customer asks to return an item, this service decides what happens: **approve it automatically**,
send it for **manual review**, or **reject** it, with the reasons a support agent sees. The decision depends on
the category's return rules, the return window, the return history of every account linked to the customer,
the value being returned, and how new the account is.

Several integrated tests fail. Find out why and fix the service so that they pass.

## API
`POST /api/returns/evaluate` with `{"orderId", "itemId", "reason", "requestedAt"}`. `requestedAt` is a date like
`2026-11-15` (today when left out). `reason` is one of `DAMAGED`, `WRONG_ITEM`, `NOT_AS_DESCRIBED`,
`CHANGED_MIND`, `NO_LONGER_NEEDED`.

```
200 {"returnId": "RET-0003", "decision": "MANUAL_REVIEW", "riskScore": 35,
     "reasons": ["REASON_DISCRETIONARY", "ORDER_VALUE_MODERATE", "NEW_ACCOUNT"],
     "messages": ["The customer changed their mind or no longer needs the item", "...", "..."]}
400 {"message": "orderId, itemId and reason are required"} · "Invalid return reason" · "requestedAt must be a date like 2026-11-15"
404 {"message": "Order not found"} · "Item not found in order"
```

`GET /api/returns/customer/{customerId}`: every return request of that customer (404 "Customer not found").

Every evaluation is saved in the return history: `AUTO_APPROVE` as `APPROVED`, `MANUAL_REVIEW` as
`PENDING_REVIEW`, `REJECT` as `REJECTED`, with `amount` = price x quantity and `date` = `requestedAt`.

## How a request is evaluated

### 1. Eligibility (in this order; the first rule broken rejects the request with riskScore 0 and that one reason)
| Rule | Reason code |
|---|---|
| The order must be delivered | `NOT_DELIVERED` |
| The item must not already have an `APPROVED` or `PENDING_REVIEW` return (a `REJECTED` one doesn't count) | `ALREADY_RETURNED` |
| The category must be returnable. Categories match whatever their case ("Electronics" = "electronics"); unknown categories are not returnable | `NON_RETURNABLE_CATEGORY` |
| The request must be inside the category's window: whole days from delivery to the request, and the last day still counts (day 30 of a 30-day window is fine, day 31 isn't) | `RETURN_WINDOW_EXPIRED` |

| Category | Returnable | Window |
|---|---|---|
| Electronics | yes | 30 days |
| Apparel | yes | 45 days |
| Home & Kitchen | yes | 30 days |
| Books | yes | 14 days |
| Jewelry | yes | 15 days |
| Grocery, Digital Content, Gift Cards | no | |

### 2. Linked accounts and return history
Accounts are linked when they share a household, address or payment method (`linkedAccountIds`). Links chain:
if A is linked to B and B to C, then A, B and C are one group. The history is every **approved** return of any
account in the group made 0 to 90 days before the request (90 days still counts, 91 doesn't).

### 3. Risk score (0 to 100, capped at 100)
| Rule | Points | Reason code |
|---|---|---|
| Reason `NOT_AS_DESCRIBED` | +10 | `REASON_NOT_AS_DESCRIBED` |
| Reason `CHANGED_MIND` or `NO_LONGER_NEEDED` | +20 | `REASON_DISCRETIONARY` |
| Value (price x quantity) 500 or more | +25 | `ORDER_VALUE_HIGH` |
| Value 200 or more (below 500) | +15 | `ORDER_VALUE_ELEVATED` |
| Value 50 or more (below 200) | +5 | `ORDER_VALUE_MODERATE` |
| History: 10 per approved return in the group, at most 40 | +10 to +40 | `RETURN_FREQUENCY` |
| The group was refunded **more than** 1000 in total | +15 | `REFUND_TOTAL_HIGH` |
| The customer's account is less than 30 days old on the request date | +10 | `NEW_ACCOUNT` |

Reasons are listed in the order of this table.

### 4. Decision
| Score | Decision |
|---|---|
| 0 to 29 | `AUTO_APPROVE` |
| 30 to 69 | `MANUAL_REVIEW` |
| 70 to 100 | `REJECT`, and `HIGH_RISK` is added at the end of the reasons |

Each reason code comes with its message (`messages`, same order).

## Getting started
```
npm install          # already done in this environment
npm test             # run the tests
npm start            # http://localhost:5000, with data/seed.json loaded
```

Example:
```
curl -s -X POST localhost:5000/api/returns/evaluate -H 'Content-Type: application/json' \
     -d '{"orderId":"O-5001","itemId":"I-1","reason":"CHANGED_MIND","requestedAt":"2026-11-15"}'
```

## Project structure
```
app.js, server.js
config/returnPolicy.js            categories: returnable and window
config/riskRules.js               points and thresholds
data/store.js, data/seed.json     the in-memory store and the sample data
utils/dates.js                    calendar-day arithmetic
services/eligibilityService.js    step 1
services/linkedAccountService.js  step 2: the account group
services/returnHistoryService.js  step 2: approved returns in the last 90 days
services/riskScoringService.js    step 3
services/decisionService.js       step 4
services/reasonCodes.js           reason codes and their messages
controllers/returnController.js   the API
routes/returnRoutes.js
tests/                            the integrated tests (read-only)
```

## Additional Information
- The data lives in an in-memory store standing in for the customer, order and returns databases. The app loads
  `data/seed.json` when it starts; each test loads its own data.
- The code repository may intentionally contain other issues that are unrelated to this specific task.
  Please focus only on the described task requirements and address bugs or errors directly associated with them.
