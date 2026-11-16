// An in-memory store standing in for the customer, order and returns databases.
// reset() loads a data set (data/seed.json when the server starts; the tests load their own).
let state = { customers: new Map(), orders: new Map(), returns: [] };
let nextReturnId = 1;

const reset = (data = {}) => {
  state = {
    customers: new Map((data.customers || []).map((c) => [c.id, { linkedAccountIds: [], ...c }])),
    orders: new Map((data.orders || []).map((o) => [o.id, o])),
    returns: (data.returns || []).map((r) => ({ ...r })),
  };
  nextReturnId = state.returns.length + 1;
};

const getCustomer = (id) => state.customers.get(id) || null;
const getOrder = (id) => state.orders.get(id) || null;
const returnsForCustomer = (customerId) => state.returns.filter((r) => r.customerId === customerId);
const returnsForItem = (orderId, itemId) => state.returns.filter((r) => r.orderId === orderId && r.itemId === itemId);

const addReturn = (record) => {
  const saved = { id: `RET-${String(nextReturnId++).padStart(4, '0')}`, ...record };
  state.returns.push(saved);
  return saved;
};

module.exports = { reset, getCustomer, getOrder, returnsForCustomer, returnsForItem, addReturn };
