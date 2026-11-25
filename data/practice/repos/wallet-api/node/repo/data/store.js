// An in-memory store standing in for the wallet database. Balances are whole rupees.
// reset() loads a data set (data/seed.json when the server starts; the tests load their own).
let wallets = new Map();
let transactions = [];
let nextTx = 1;

const reset = (data = {}) => {
  wallets = new Map((data.wallets || []).map((w) => [w.id, { ...w }]));
  transactions = (data.transactions || []).map((t) => ({ ...t }));
  nextTx = transactions.length + 1;
};

const getWallet = (id) => wallets.get(id) || null;
const transactionsOf = (walletId) => transactions.filter((t) => t.walletId === walletId);

// Changes a wallet's balance and records the transaction.
const record = (wallet, type, amount, at, counterparty = null) => {
  wallet.balance += type === 'deposit' || type === 'transfer_in' ? amount : -amount;
  const tx = { id: `TX${nextTx++}`, walletId: wallet.id, type, amount, balanceAfter: wallet.balance, counterparty, at };
  transactions.push(tx);
  return tx;
};

module.exports = { reset, getWallet, transactionsOf, record };
