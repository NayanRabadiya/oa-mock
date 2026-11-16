const { MANUAL_REVIEW_FROM, REJECT_FROM } = require('../config/riskRules');
const { messagesFor } = require('./reasonCodes');

// What the service decides, and what it stores in the return history for that decision.
const STATUS_FOR = { AUTO_APPROVE: 'APPROVED', MANUAL_REVIEW: 'PENDING_REVIEW', REJECT: 'REJECTED' };

const decide = (score, reasons) => {
  let decision = 'AUTO_APPROVE';
  const codes = [...reasons];

  if (score >= REJECT_FROM) {
    decision = 'REJECT';
    codes.push('HIGH_RISK');
  } else if (score >= MANUAL_REVIEW_FROM) {
    decision = 'MANUAL_REVIEW';
  }

  return { decision, riskScore: score, reasons: codes, messages: messagesFor(codes) };
};

// A request that breaks an eligibility rule is rejected with just that reason.
const ineligible = (code) => ({ decision: 'REJECT', riskScore: 0, reasons: [code], messages: messagesFor([code]) });

module.exports = { decide, ineligible, STATUS_FOR };
