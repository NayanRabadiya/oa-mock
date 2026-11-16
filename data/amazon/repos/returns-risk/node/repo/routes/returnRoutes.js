const express = require('express');
const { evaluateReturn, getCustomerReturns } = require('../controllers/returnController');

const router = express.Router();

router.post('/evaluate', evaluateReturn);
router.get('/customer/:customerId', getCustomerReturns);

module.exports = router;
