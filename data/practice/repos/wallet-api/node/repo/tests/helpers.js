// Shared setup for the wallet tests: three wallets, no transactions yet.
const request = require('supertest');
const app = require('../app');
const store = require('../data/store');

const fresh = () =>
  store.reset({
    wallets: [
      { id: 'W1', owner: 'Asha', balance: 1000, status: 'active' },
      { id: 'W2', owner: 'Bilal', balance: 200, status: 'active' },
      { id: 'W3', owner: 'Chen', balance: 500, status: 'frozen' },
    ],
    transactions: [],
  });

const deposit = (id, amount, at = '2026-11-15T09:00:00Z') => request(app).post(`/api/wallets/${id}/deposit`).send({ amount, at });
const withdraw = (id, amount, at = '2026-11-15T09:00:00Z') => request(app).post(`/api/wallets/${id}/withdraw`).send({ amount, at });
const send = (from, to, amount, at = '2026-11-15T10:00:00Z') => request(app).post('/api/transfers').send({ from, to, amount, at });
const wallet = (id) => request(app).get(`/api/wallets/${id}`);
const history = (id, query = '') => request(app).get(`/api/wallets/${id}/transactions${query}`);

module.exports = { fresh, deposit, withdraw, send, wallet, history, request, app };
