// Shared setup for the support desk tests: two agents and no tickets.
const request = require('supertest');
const app = require('../app');
const store = require('../data/store');

const fresh = () =>
  store.reset({
    agents: [{ id: 'A1', name: 'Meera', maxOpen: 2 }, { id: 'A2', name: 'Tomas', maxOpen: 3 }],
    tickets: [],
  });

const create = (priority, createdAt = '2026-11-15T09:00:00Z', title = 'Help') =>
  request(app).post('/api/tickets').send({ title, customer: 'acme', priority, createdAt });

const assign = (id, agentId) => request(app).post(`/api/tickets/${id}/assign`).send({ agentId });
const move = (id, status, at = '2026-11-15T12:00:00Z') => request(app).post(`/api/tickets/${id}/status`).send({ status, at });
const list = (query = '') => request(app).get(`/api/tickets${query}`);
const overdue = (now) => request(app).get(`/api/tickets/overdue?now=${now}`);

module.exports = { fresh, create, assign, move, list, overdue, request, app };
