const express = require('express');
const c = require('../controllers/ticketController');

const router = express.Router();

router.get('/tickets', c.listTickets);
router.get('/tickets/overdue', c.overdueTickets);
router.post('/tickets', c.createTicket);
router.post('/tickets/:id/assign', c.assignTicket);
router.post('/tickets/:id/status', c.changeStatus);

module.exports = router;
