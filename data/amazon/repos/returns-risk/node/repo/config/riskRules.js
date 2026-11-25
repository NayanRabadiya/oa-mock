// Points that make up a return's risk score (0-100), and the decision thresholds.
module.exports = {
  REASON_POINTS: {
    DAMAGED: 0,
    WRONG_ITEM: 0,
    NOT_AS_DESCRIBED: 10,
    CHANGED_MIND: 20,
    NO_LONGER_NEEDED: 20,
  },
  // the value being returned is price x quantity
  VALUE_TIERS: [
    { min: 500, points: 25, code: 'ORDER_VALUE_HIGH' },
    { min: 200, points: 15, code: 'ORDER_VALUE_ELEVATED' },
    { min: 50, points: 5, code: 'ORDER_VALUE_MODERATE' },
  ],
  HISTORY_DAYS: 90,              // approved returns in the 90 days before the request
  POINTS_PER_RECENT_RETURN: 10,
  MAX_HISTORY_POINTS: 40,
  REFUND_TOTAL_LIMIT: 1000,      // more than this refunded in the 90 days
  REFUND_TOTAL_POINTS: 15,
  NEW_ACCOUNT_DAYS: 30,          // account created less than 30 days before the request
  NEW_ACCOUNT_POINTS: 10,
  MAX_SCORE: 100,
  MANUAL_REVIEW_FROM: 30,        // 30-69: manual review
  REJECT_FROM: 70,               // 70 and above: reject
};
