const store = require('../data/store');
const { PRIORITIES, STATUSES } = require('../config/rules');
const { sortTickets, filterTickets } = require('../services/ticketService');
const { canTake } = require('../services/assignmentService');
const { canMove } = require('../services/workflowService');
const { isOverdue } = require('../services/slaService');
const { isIsoTime, now } = require('../utils/time');

const fail = (res, status, message) => res.status(status).json({ message });

// GET /api/tickets?status=&priority=&assigneeId=
const listTickets = (req, res) => {
  const { status, priority, assigneeId } = req.query;
  res.json(sortTickets(filterTickets(store.allTickets(), { status, priority, assigneeId })));
};

// POST /api/tickets  { title, customer, priority, createdAt? }
const createTicket = (req, res) => {
  const { title, customer, priority } = req.body || {};
  const createdAt = (req.body && req.body.createdAt) || now();
  if (!title || !customer || !priority) {
    return fail(res, 400, 'title, customer and priority are required');
  }
  if (!PRIORITIES.includes(priority)) {
    return fail(res, 400, 'Invalid priority');
  }
  if (!isIsoTime(createdAt)) {
    return fail(res, 400, 'createdAt must be a time like 2026-11-15T09:30:00Z');
  }
  res.status(201).json(store.addTicket({ title, customer, priority, createdAt }));
};

// POST /api/tickets/:id/assign  { agentId }
const assignTicket = (req, res) => {
  const ticket = store.getTicket(req.params.id);
  if (!ticket) {
    return fail(res, 404, 'Ticket not found');
  }
  const agent = store.getAgent((req.body || {}).agentId);
  if (!agent) {
    return fail(res, 404, 'Agent not found');
  }
  if (!['open', 'in_progress'].includes(ticket.status)) {
    return fail(res, 409, 'Only open or in-progress tickets can be assigned');
  }
  if (!canTake(agent, ticket)) {
    return fail(res, 409, 'Agent has too many open tickets');
  }
  ticket.assigneeId = agent.id;
  if (ticket.status === 'open') {
    ticket.status = 'in_progress';
  }
  res.json(ticket);
};

// POST /api/tickets/:id/status  { status, at? }
const changeStatus = (req, res) => {
  const ticket = store.getTicket(req.params.id);
  if (!ticket) {
    return fail(res, 404, 'Ticket not found');
  }
  const { status } = req.body || {};
  const at = (req.body && req.body.at) || now();
  if (!STATUSES.includes(status)) {
    return fail(res, 400, 'Invalid status');
  }
  if (!canMove(ticket.status, status)) {
    return fail(res, 409, `Cannot move a ticket from ${ticket.status} to ${status}`);
  }
  ticket.status = status;
  if (status === 'resolved') {
    ticket.resolvedAt = at;
  } else if (status === 'in_progress') {
    ticket.resolvedAt = null;
  }
  res.json(ticket);
};

// GET /api/tickets/overdue?now=
const overdueTickets = (req, res) => {
  const at = req.query.now || now();
  if (!isIsoTime(at)) {
    return fail(res, 400, 'now must be a time like 2026-11-15T09:30:00Z');
  }
  res.json(sortTickets(store.allTickets().filter((t) => isOverdue(t, at))));
};

module.exports = { listTickets, createTicket, assignTicket, changeStatus, overdueTickets };
