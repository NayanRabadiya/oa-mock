const { HISTORY_DAYS } = require('../config/riskRules');
const { daysBetween } = require('../utils/dates');
const store = require('../data/store');

// Approved (refunded) returns of a group of accounts in the HISTORY_DAYS days before `requestedAt`.
const recentRefunds = (accountIds, requestedAt) => {
  const refunds = [];
  for (const id of accountIds) {
    for (const ret of store.returnsForCustomer(id)) {
      const age = daysBetween(ret.date, requestedAt);
      if (ret.status === 'APPROVED' && age >= 0 && age <= HISTORY_DAYS) {
        refunds.push(ret);
      }
    }
  }
  return refunds;
};

const summarize = (accountIds, requestedAt) => {
  const refunds = recentRefunds(accountIds, requestedAt);
  return {
    count: refunds.length,
    total: refunds.reduce((sum, r) => sum + Number(r.amount || 0), 0),
  };
};

module.exports = { recentRefunds, summarize };
