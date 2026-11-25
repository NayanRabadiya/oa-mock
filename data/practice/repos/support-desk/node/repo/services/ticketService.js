const { PRIORITIES } = require('../config/rules');

// Most urgent first; tickets of the same priority oldest first (then by id).
const compareTickets = (a, b) =>
  PRIORITIES.indexOf(a.priority) - PRIORITIES.indexOf(b.priority) ||
  Date.parse(b.createdAt) - Date.parse(a.createdAt) ||
  a.id.localeCompare(b.id, undefined, { numeric: true });

const sortTickets = (tickets) => tickets.slice().sort(compareTickets);

// Keeps the tickets that match every filter given ({ status, priority, assigneeId }).
const filterTickets = (tickets, filters) =>
  tickets.filter((t) => Object.entries(filters).every(([key, value]) => value === undefined || t[key] === value));

module.exports = { sortTickets, filterTickets };
