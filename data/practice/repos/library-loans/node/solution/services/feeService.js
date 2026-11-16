const { LOAN_DAYS, FEE_PER_DAY, MAX_FEE } = require('../config/loanRules');
const { daysBetween } = require('../utils/dates');

// Days a return is late, and the fee for it. A book returned on its due date (day 14) is on time.
const lateFee = (borrowedAt, returnedAt) => {
  const daysLate = Math.max(0, daysBetween(borrowedAt, returnedAt) - LOAN_DAYS);
  return { daysLate, fee: Math.min(daysLate * FEE_PER_DAY, MAX_FEE) };
};

module.exports = { lateFee };
