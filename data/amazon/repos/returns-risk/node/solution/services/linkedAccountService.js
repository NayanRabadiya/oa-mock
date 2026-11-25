const store = require('../data/store');

// Accounts are linked when they share a household, address or payment method. Links can chain
// (A is linked to B, B to C), and every account in the chain belongs to the same group.
// Returns the ids of the whole group, the customer first.
const getAccountGroup = (customerId) => {
  const group = [customerId];
  const seen = new Set(group);

  for (let i = 0; i < group.length; i++) {
    const customer = store.getCustomer(group[i]);
    for (const linkedId of (customer && customer.linkedAccountIds) || []) {
      if (!seen.has(linkedId)) {
        seen.add(linkedId);
        group.push(linkedId);
      }
    }
  }

  return group;
};

module.exports = { getAccountGroup };
