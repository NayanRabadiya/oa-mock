// Shared setup for the library tests: a fresh store with three books and two members.
const request = require('supertest');
const app = require('../app');
const store = require('../data/store');

const fresh = () =>
  store.reset({
    books: [
      { id: 'B1', title: 'The Pragmatic Programmer', copies: 2 },
      { id: 'B2', title: 'Clean Code', copies: 1 },
      { id: 'B3', title: 'Refactoring', copies: 5 },
    ],
    members: [{ id: 'M1', name: 'Asha' }, { id: 'M2', name: 'Bilal' }],
    loans: [],
  });

const borrow = (memberId, bookId, borrowedAt = '2026-11-01') =>
  request(app).post('/api/loans').send({ memberId, bookId, borrowedAt });

const giveBack = (loanId, returnedAt) => request(app).post(`/api/loans/${loanId}/return`).send({ returnedAt });

const available = async (bookId) => (await request(app).get('/api/books')).body.find((b) => b.id === bookId).available;

module.exports = { fresh, borrow, giveBack, available, request, app };
