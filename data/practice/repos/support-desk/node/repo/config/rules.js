// The support desk's rules.
module.exports = {
  // Most urgent first.
  PRIORITIES: ['urgent', 'high', 'medium', 'low'],
  STATUSES: ['open', 'in_progress', 'resolved', 'closed'],
  // A ticket that isn't resolved within this many hours of being created is overdue.
  SLA_HOURS: { urgent: 4, high: 24, medium: 72, low: 168 },
};
