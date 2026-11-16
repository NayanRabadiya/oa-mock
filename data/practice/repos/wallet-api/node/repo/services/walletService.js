const store = require('../data/store');
const { WalletError } = require('./walletErrors');

const isAmount = (value) => Number.isInteger(value) && value > 0;

const walletOrFail = (id) => {
  const wallet = store.getWallet(id);
  if (!wallet) throw new WalletError(404, 'Wallet not found');
  return wallet;
};

const activeOrFail = (wallet) => {
  if (wallet.status !== 'active') throw new WalletError(409, 'Wallet is frozen');
};

const deposit = (id, amount, at) => {
  if (!isAmount(amount)) throw new WalletError(400, 'amount must be a positive whole number');
  const wallet = walletOrFail(id);
  activeOrFail(wallet);
  return { wallet, transaction: store.record(wallet, 'deposit', amount, at) };
};

const withdraw = (id, amount, at) => {
  if (!isAmount(amount)) throw new WalletError(400, 'amount must be a positive whole number');
  const wallet = walletOrFail(id);
  activeOrFail(wallet);
  if (wallet.balance < amount) throw new WalletError(409, 'Insufficient funds');
  return { wallet, transaction: store.record(wallet, 'withdrawal', amount, at) };
};

// Newest first (then the later transaction first).
const newestFirst = (a, b) => Date.parse(b.at) - Date.parse(a.at) || Number(b.id.slice(2)) - Number(a.id.slice(2));

const history = (id, type, limit) => {
  walletOrFail(id);
  return store.transactionsOf(id).filter((t) => !type || t.type === type).sort(newestFirst).slice(0, limit);
};

module.exports = { isAmount, walletOrFail, activeOrFail, deposit, withdraw, history };
