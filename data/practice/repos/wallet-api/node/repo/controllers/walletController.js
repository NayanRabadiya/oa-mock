const { WalletError } = require('../services/walletErrors');
const walletService = require('../services/walletService');
const { transfer } = require('../services/transferService');
const { DEFAULT_PAGE, MAX_PAGE, TYPES } = require('../config/limits');
const { isIsoTime, now } = require('../utils/time');

// Runs a handler and turns a WalletError into its HTTP answer.
const handle = (fn) => (req, res) => {
  try {
    fn(req, res);
  } catch (err) {
    if (err instanceof WalletError) return res.status(err.status).json({ message: err.message });
    console.error(err);
    res.status(500).json({ message: 'Server error' });
  }
};

const timeOf = (body) => {
  const at = (body && body.at) || now();
  if (!isIsoTime(at)) throw new WalletError(400, 'at must be a time like 2026-11-15T09:30:00Z');
  return at;
};

// GET /api/wallets/:id
const getWallet = handle((req, res) => res.json(walletService.walletOrFail(req.params.id)));

// POST /api/wallets/:id/deposit  { amount, at? }
const deposit = handle((req, res) => res.json(walletService.deposit(req.params.id, (req.body || {}).amount, timeOf(req.body))));

// POST /api/wallets/:id/withdraw  { amount, at? }
const withdraw = handle((req, res) => res.json(walletService.withdraw(req.params.id, (req.body || {}).amount, timeOf(req.body))));

// POST /api/transfers  { from, to, amount, at? }
const createTransfer = handle((req, res) => {
  const { from, to, amount } = req.body || {};
  res.status(201).json(transfer(from, to, amount, timeOf(req.body)));
});

// GET /api/wallets/:id/transactions?type=&limit=
const listTransactions = handle((req, res) => {
  const type = req.query.kind;
  const limit = req.query.limit === undefined ? DEFAULT_PAGE : Number(req.query.limit);
  if (type !== undefined && !TYPES.includes(type)) throw new WalletError(400, 'Invalid transaction type');
  if (!Number.isInteger(limit) || limit < 1 || limit > MAX_PAGE) throw new WalletError(400, `limit must be between 1 and ${MAX_PAGE}`);
  res.json(walletService.history(req.params.id, type, limit));
});

module.exports = { getWallet, deposit, withdraw, createTransfer, listTransactions };
