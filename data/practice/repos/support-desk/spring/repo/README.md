# Support Desk API (Spring Boot)

## Overview
A support team tracks customer tickets with this API: tickets come in with a priority, get assigned to agents,
move through a fixed workflow and must be resolved within a deadline that depends on their priority.

Several integrated tests fail. Find out why and fix the API so that every test passes.

## API
| Request | Response |
|---|---|
| `GET /api/tickets?status=&priority=&assigneeId=` | the tickets matching every filter given, in queue order (below) |
| `POST /api/tickets` `{"title", "customer", "priority", "createdAt"}` | 201 with the ticket: `{"id", "title", "customer", "priority", "status": "open", "assigneeId": null, "createdAt", "resolvedAt": null}` |
| `POST /api/tickets/{id}/assign` `{"agentId"}` | 200 with the ticket, assigned; an open ticket becomes `in_progress` |
| `POST /api/tickets/{id}/status` `{"status", "at"}` | 200 with the ticket in its new status |
| `GET /api/tickets/overdue?now=` | the overdue tickets at that time, in queue order |

Times look like `2026-11-15T09:30:00Z` (UTC; now when left out). Errors come back as `{"message": ...}`:
400 "title, customer and priority are required" · "Invalid priority" · "Invalid status" · a bad time;
404 "Ticket not found" · "Agent not found";
409 "Agent has too many open tickets" · "Only open or in-progress tickets can be assigned" · "Cannot move a ticket from {from} to {to}".

## Rules
- **Priorities**, most urgent first: `urgent`, `high`, `medium`, `low`.
- **Queue order**: by priority, most urgent first; tickets with the same priority oldest first (then by id).
- **Agent limit**: each agent has `maxOpen`. An agent can take a ticket only while they have fewer than `maxOpen`
  unfinished tickets (`open` or `in_progress`) other than this one. Resolved and closed tickets don't count.
- **Workflow**: `open` → `in_progress` → `resolved` → `closed`. A resolved ticket can be reopened (back to
  `in_progress`), which clears `resolvedAt`. Closed is final. Any other move is refused.
- **SLA**: a ticket must be resolved within **4** hours (urgent), **24** (high), **72** (medium) or **168** (low)
  of being created. An unfinished ticket is overdue once **more than** that many hours have passed.

## Getting started
```
mvn test               # run the tests (the dependencies are already downloaded in this environment)
mvn spring-boot:run    # http://localhost:5000, with src/main/resources/seed.json loaded
```

## Project structure
```
src/main/java/com/desk/
  DeskApplication.java
  config/DeskRules.java                priorities, statuses, SLA hours
  store/DeskStore.java, seed/          the in-memory store; seed.json is loaded at start-up
  model/                               agents and tickets
  util/Times.java                      ISO times
  service/TicketService.java           queue order, filters
  service/AssignmentService.java       agent workload and limit
  service/WorkflowService.java         which status can follow which
  service/SlaService.java              overdue tickets
  controller/TicketController.java     the API
src/test/java/com/desk/                the integrated tests (read-only)
```

## Additional Information
- The data lives in an in-memory store standing in for the help desk database. The app loads `src/main/resources/seed.json` when it
  starts; each test loads its own data.
- The code repository may intentionally contain other issues that are unrelated to this specific task.
  Please focus only on the described task requirements and address bugs or errors directly associated with them.
