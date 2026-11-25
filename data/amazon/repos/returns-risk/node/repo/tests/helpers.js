// Shared setup for the return/risk tests: a fresh store with linked accounts, plus helpers to add
// orders and past returns and to call the API.
const request = require('supertest');
const app = require('../app');
const store = require('../data/store');

const TODAY = '2026-11-15';

// C1 - C2 - C3 are linked in a chain; C5 has no links; C9 opened their account on 2026-11-01.
const baseCustomers = () => [
  { id: 'C1', name: 'Asha', createdAt: '2024-01-01', linkedAccountIds: ['C2'] },
  { id: 'C2', name: 'Bilal', createdAt: '2024-01-01', linkedAccountIds: ['C1', 'C3'] },
  { id: 'C3', name: 'Chen', createdAt: '2024-01-01', linkedAccountIds: ['C2'] },
  { id: 'C5', name: 'Dev', createdAt: '2024-01-01', linkedAccountIds: [] },
  { id: 'C9', name: 'Esha', createdAt: '2026-11-01', linkedAccountIds: [] },
];

let data;
const fresh = () => {
  data = { customers: baseCustomers(), orders: [], returns: [] };
  store.reset(data);
};

// An order with one item (id I-1) unless `items` is given.
const order = (id, customerId, { deliveredAt = '2026-11-01', status = 'DELIVERED', category = 'Electronics', price = 40, quantity = 1, items } = {}) => {
  data.orders.push({ id, customerId, status, deliveredAt, items: items || [{ id: 'I-1', name: 'Item', category, price, quantity }] });
  store.reset(data);
};

// A past return in the history.
const pastReturn = (customerId, { status = 'APPROVED', amount = 100, date = '2026-10-20', orderId = 'OLD-' + (data.returns.length + 1), itemId = 'I-1' } = {}) => {
  data.returns.push({ id: 'R' + (data.returns.length + 1), customerId, orderId, itemId, status, amount, date });
  store.reset(data);
};

const evaluate = (orderId, reason = 'DAMAGED', extra = {}) =>
  request(app).post('/api/returns/evaluate').send({ orderId, itemId: 'I-1', reason, requestedAt: TODAY, ...extra });

module.exports = { fresh, order, pastReturn, evaluate, request, app, TODAY };
