const { SLA_HOURS } = require('../config/rules');
const { MS_PER_HOUR } = require('../utils/time');

const UNFINISHED = ['open', 'in_progress'];

// A ticket is overdue when it is still unfinished more than SLA_HOURS[priority] hours after it was created.
const hoursOpen = (ticket, now) => (Date.parse(now) - Date.parse(ticket.createdAt)) / MS_PER_HOUR;

const isOverdue = (ticket, now) => UNFINISHED.includes(ticket.status) && hoursOpen(ticket, now) > SLA_HOURS[ticket.priority];

module.exports = { hoursOpen, isOverdue };
