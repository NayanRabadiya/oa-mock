// Every reason code the service can return, with the text shown to support agents.
const REASON_MESSAGES = {
  NOT_DELIVERED: "The order hasn't been delivered yet",
  ALREADY_RETURNED: 'This item already has an approved or pending return',
  NON_RETURNABLE_CATEGORY: "Items in this category can't be returned",
  RETURN_WINDOW_EXPIRED: 'The return window for this category has passed',
  REASON_NOT_AS_DESCRIBED: 'The customer says the item is not as described',
  REASON_DISCRETIONARY: 'The customer changed their mind or no longer needs the item',
  ORDER_VALUE_HIGH: 'The return is worth 500 or more',
  ORDER_VALUE_ELEVATED: 'The return is worth 200 or more',
  ORDER_VALUE_MODERATE: 'The return is worth 50 or more',
  RETURN_FREQUENCY: 'Linked accounts had approved returns in the last 90 days',
  REFUND_TOTAL_HIGH: 'Linked accounts were refunded more than 1000 in the last 90 days',
  NEW_ACCOUNT: 'The account is less than 30 days old',
  HIGH_RISK: 'The risk score is 70 or more',
};

const messagesFor = (codes) => codes.map((code) => REASON_MESSAGES[code] || code);

module.exports = { REASON_MESSAGES, messagesFor };
