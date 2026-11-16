// An in-memory store standing in for the help desk database.
// reset() loads a data set (data/seed.json when the server starts; the tests load their own).
let agents = new Map();
let tickets = [];
let nextId = 1;

const reset = (data = {}) => {
  agents = new Map((data.agents || []).map((a) => [a.id, { ...a }]));
  tickets = (data.tickets || []).map((t) => ({ assigneeId: null, resolvedAt: null, ...t }));
  nextId = tickets.length + 1;
};

const getAgent = (id) => agents.get(id) || null;
const allTickets = () => tickets.slice();
const getTicket = (id) => tickets.find((t) => t.id === id) || null;

const addTicket = (ticket) => {
  const saved = { id: `T${nextId++}`, status: 'open', assigneeId: null, resolvedAt: null, ...ticket };
  tickets.push(saved);
  return saved;
};

module.exports = { reset, getAgent, allTickets, getTicket, addTicket };
