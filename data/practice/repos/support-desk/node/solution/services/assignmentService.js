const store = require('../data/store');

const ACTIVE = ['open', 'in_progress'];

// How many unfinished tickets an agent has, not counting `exceptId`.
const workload = (agentId, exceptId) =>
  store.allTickets().filter((t) => t.assigneeId === agentId && t.id !== exceptId && ACTIVE.includes(t.status)).length;

// An agent can take a ticket while they have fewer than maxOpen unfinished tickets.
const canTake = (agent, ticket) => workload(agent.id, ticket.id) < agent.maxOpen;

module.exports = { workload, canTake };
