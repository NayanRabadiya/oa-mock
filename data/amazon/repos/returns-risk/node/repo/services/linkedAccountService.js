const store = require('../data/store');

// Accounts are linked when they share a household, address or payment method. Links can chain
// (A is linked to B, B to C), and every account in the chain belongs to the same group.
// Returns the ids of the whole group, the customer first.
const getAccountGroup = (customerId) => {
  const customer = store.getCustomer(customerId);
  const linked = (customer && customer.linkedAccountIds) || [];

  return [customerId, ...linked.filter((id) => id !== customerId)];
};

module.exports = { getAccountGroup };
