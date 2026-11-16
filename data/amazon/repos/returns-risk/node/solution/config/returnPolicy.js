// Which product categories can be returned, and within how many days of delivery.
// Orders store the category the way the catalogue shows it ("Electronics", "Home & Kitchen" ...);
// policy keys are lowercase.
const RETURN_POLICY = {
  electronics: { returnable: true, windowDays: 30 },
  apparel: { returnable: true, windowDays: 45 },
  'home & kitchen': { returnable: true, windowDays: 30 },
  books: { returnable: true, windowDays: 14 },
  jewelry: { returnable: true, windowDays: 15 },
  grocery: { returnable: false, windowDays: 0 },
  'digital content': { returnable: false, windowDays: 0 },
  'gift cards': { returnable: false, windowDays: 0 },
};

// Unknown categories can't be returned.
const NOT_RETURNABLE = { returnable: false, windowDays: 0 };

const getPolicy = (category) => {
  const key = String(category || '').trim().toLowerCase();
  return RETURN_POLICY[key] || NOT_RETURNABLE;
};

module.exports = { RETURN_POLICY, getPolicy };
