const express = require('express');
const c = require('../controllers/walletController');

const router = express.Router();

router.get('/wallets/:id', c.getWallet);
router.post('/wallets/:id/deposit', c.deposit);
router.post('/wallets/:id/withdraw', c.withdraw);
router.get('/wallets/:id/transactions', c.listTransactions);
router.post('/transfers', c.createTransfer);

module.exports = router;
