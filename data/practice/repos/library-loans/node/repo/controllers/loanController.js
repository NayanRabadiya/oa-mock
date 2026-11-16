const store = require('../data/store');
const { availableCopies, cannotBorrow } = require('../services/loanService');
const { lateFee } = require('../services/feeService');
const { isIsoDate, today } = require('../utils/dates');

// GET /api/books  every book, with how many copies are on the shelf
const listBooks = (req, res) => {
  res.json(store.allBooks().map((b) => ({ ...b, available: availableCopies(b) })));
};

// POST /api/loans  { memberId, bookId, borrowedAt? }
const borrowBook = (req, res) => {
  const { memberId, bookId } = req.body || {};
  const borrowedAt = (req.body && req.body.borrowedAt) || today();
  if (!memberId || !bookId) {
    return res.status(400).json({ message: 'memberId and bookId are required' });
  }
  if (!isIsoDate(borrowedAt)) {
    return res.status(400).json({ message: 'borrowedAt must be a date like 2026-11-15' });
  }
  const member = store.getMember(memberId);
  if (!member) {
    return res.status(404).json({ message: 'Member not found' });
  }
  const book = store.getBook(bookId);
  if (!book) {
    return res.status(404).json({ message: 'Book not found' });
  }
  const problem = cannotBorrow(member, book);
  if (problem) {
    return res.status(409).json({ message: problem });
  }
  res.status(201).json(store.addLoan({ memberId, bookId, borrowedAt }));
};

// POST /api/loans/:loanId/return  { returnedAt? }
const returnBook = (req, res) => {
  const loan = store.getLoan(req.params.loanId);
  if (!loan) {
    return res.status(404).json({ message: 'Loan not found' });
  }
  if (loan.returnedAt) {
    return res.status(409).json({ message: 'Loan already returned' });
  }
  const returnedAt = (req.body && req.body.returnedAt) || today();
  if (!isIsoDate(returnedAt)) {
    return res.status(400).json({ message: 'returnedAt must be a date like 2026-11-15' });
  }
  loan.returnedAt = returnedAt;
  res.json({ loanId: loan.id, returnedAt, ...lateFee(loan.borrowedAt, returnedAt) });
};

module.exports = { listBooks, borrowBook, returnBook };
