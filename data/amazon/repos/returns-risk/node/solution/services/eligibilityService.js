const { getPolicy } = require('../config/returnPolicy');
const { daysBetween } = require('../utils/dates');
const store = require('../data/store');

// The first rule a return request breaks, as a reason code, or null when it may be returned.
// Rules are checked in this order: delivered, not already returned, returnable category, inside the window.
const checkEligibility = (order, item, requestedAt) => {
  if (order.status !== 'DELIVERED' || !order.deliveredAt) {
    return 'NOT_DELIVERED';
  }

  const previous = store.returnsForItem(order.id, item.id);
  if (previous.some((r) => r.status === 'APPROVED' || r.status === 'PENDING_REVIEW')) {
    return 'ALREADY_RETURNED';
  }

  const policy = getPolicy(item.category);
  if (!policy.returnable) {
    return 'NON_RETURNABLE_CATEGORY';
  }

  const daysSinceDelivery = daysBetween(order.deliveredAt, requestedAt);
  if (daysSinceDelivery > policy.windowDays) {
    return 'RETURN_WINDOW_EXPIRED';
  }

  return null;
};

module.exports = { checkEligibility };
