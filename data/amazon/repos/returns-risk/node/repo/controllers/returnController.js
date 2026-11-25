const store = require('../data/store');
const { REASON_POINTS } = require('../config/riskRules');
const { checkEligibility } = require('../services/eligibilityService');
const { getAccountGroup } = require('../services/linkedAccountService');
const { summarize } = require('../services/returnHistoryService');
const { scoreReturn } = require('../services/riskScoringService');
const { decide, ineligible, STATUS_FOR } = require('../services/decisionService');
const { isIsoDate, today } = require('../utils/dates');

// POST /api/returns/evaluate  { orderId, itemId, reason, requestedAt? }
const evaluateReturn = (req, res) => {
  try {
    const { orderId, itemId, reason } = req.body || {};
    const requestedAt = req.body && req.body.requestedAt !== undefined ? req.body.requestedAt : today();

    if (!orderId || !itemId || !reason) {
      return res.status(400).json({ message: 'orderId, itemId and reason are required' });
    }
    if (!Object.prototype.hasOwnProperty.call(REASON_POINTS, reason)) {
      return res.status(400).json({ message: 'Invalid return reason' });
    }
    if (!isIsoDate(requestedAt)) {
      return res.status(400).json({ message: 'requestedAt must be a date like 2026-11-15' });
    }

    const order = store.getOrder(orderId);
    if (!order) {
      return res.status(404).json({ message: 'Order not found' });
    }
    const item = (order.items || []).find((i) => i.id === itemId);
    if (!item) {
      return res.status(404).json({ message: 'Item not found in order' });
    }
    const customer = store.getCustomer(order.customerId) || { id: order.customerId };

    let result;
    const blocked = checkEligibility(order, item, requestedAt);
    if (blocked) {
      result = ineligible(blocked);
    } else {
      const group = getAccountGroup(customer.id);
      const history = summarize(group, requestedAt);
      const { score, reasons } = scoreReturn({ item, reason, customer, history, requestedAt });
      result = decide(score, reasons);
    }

    const record = store.addReturn({
      customerId: customer.id,
      orderId,
      itemId,
      status: STATUS_FOR[result.decision],
      amount: Number(item.price) * Number(item.quantity || 1),
      date: requestedAt,
      reason,
    });

    res.json({ returnId: record.id, ...result });
  } catch (error) {
    console.error('Evaluate return error:', error);
    res.status(500).json({ message: 'Server error' });
  }
};

// GET /api/returns/customer/:customerId  every return request of one customer, oldest first
const getCustomerReturns = (req, res) => {
  const customer = store.getCustomer(req.params.customerId);
  if (!customer) {
    return res.status(404).json({ message: 'Customer not found' });
  }
  res.json(store.returnsForCustomer(customer.id));
};

module.exports = { evaluateReturn, getCustomerReturns };
