// An in-memory store standing in for the library database.
// reset() loads a data set (data/seed.json when the server starts; the tests load their own).
let state = { books: new Map(), members: new Map(), loans: [] };
let nextLoanId = 1;

const reset = (data = {}) => {
  state = {
    books: new Map((data.books || []).map((b) => [b.id, b])),
    members: new Map((data.members || []).map((m) => [m.id, m])),
    loans: (data.loans || []).map((l) => ({ returnedAt: null, ...l })),
  };
  nextLoanId = state.loans.length + 1;
};

const allBooks = () => [...state.books.values()];
const getBook = (id) => state.books.get(id) || null;
const getMember = (id) => state.members.get(id) || null;
const getLoan = (id) => state.loans.find((l) => l.id === id) || null;
const openLoans = (filter) => state.loans.filter((l) => !l.returnedAt && filter(l));

const addLoan = (loan) => {
  const saved = { id: `L${nextLoanId++}`, returnedAt: null, ...loan };
  state.loans.push(saved);
  return saved;
};

module.exports = { reset, allBooks, getBook, getMember, getLoan, openLoans, addLoan };
