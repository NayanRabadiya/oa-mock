const { MAX_OPEN_LOANS } = require('../config/loanRules');
const store = require('../data/store');

// How many copies of a book are on the shelf right now.
const availableCopies = (book) => book.copies - store.openLoans((l) => l.bookId === book.id).length;

// Why a member can't borrow a book right now, or null when they can.
const cannotBorrow = (member, book) => {
  if (availableCopies(book) <= 0) {
    return 'No copies available';
  }
  const open = store.openLoans((l) => l.memberId === member.id);
  if (open.length >= MAX_OPEN_LOANS) {
    return 'Loan limit reached';
  }
  return null;
};

module.exports = { availableCopies, cannotBorrow };
