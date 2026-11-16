const rules = require('../config/riskRules');
const { daysBetween } = require('../utils/dates');

// Adds up the risk points for one return. Returns { score, reasons } where reasons are the codes of
// every rule that added points, in this order: return reason, value, history, refund total, account age.
const scoreReturn = ({ item, reason, customer, history, requestedAt }) => {
  let score = 0;
  const reasons = [];

  const reasonPoints = rules.REASON_POINTS[reason] || 0;
  if (reasonPoints > 0) {
    score += reasonPoints;
    reasons.push(reason === 'NOT_AS_DESCRIBED' ? 'REASON_NOT_AS_DESCRIBED' : 'REASON_DISCRETIONARY');
  }

  const value = Number(item.price);
  const tier = rules.VALUE_TIERS.find((t) => value >= t.min);
  if (tier) {
    score += tier.points;
    reasons.push(tier.code);
  }

  if (history.count > 0) {
    score += Math.min(history.count * rules.POINTS_PER_RECENT_RETURN, rules.MAX_HISTORY_POINTS);
    reasons.push('RETURN_FREQUENCY');
  }

  if (history.total > rules.REFUND_TOTAL_LIMIT) {
    score += rules.REFUND_TOTAL_POINTS;
    reasons.push('REFUND_TOTAL_HIGH');
  }

  if (customer.createdAt && daysBetween(customer.createdAt, requestedAt) < rules.NEW_ACCOUNT_DAYS) {
    score += rules.NEW_ACCOUNT_POINTS;
    reasons.push('NEW_ACCOUNT');
  }

  return { score: Math.min(score, rules.MAX_SCORE), reasons };
};

module.exports = { scoreReturn };
