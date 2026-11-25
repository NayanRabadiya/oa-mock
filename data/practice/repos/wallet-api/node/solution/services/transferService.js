const store = require('../data/store');
const { WalletError } = require('./walletErrors');
const { isAmount, walletOrFail, activeOrFail } = require('./walletService');

// Moves money between two wallets. Either both sides change or neither does: every check runs before any
// balance changes.
const transfer = (fromId, toId, amount, at) => {
  if (!fromId || !toId || amount === undefined) throw new WalletError(400, 'from, to and amount are required');
  if (!isAmount(amount)) throw new WalletError(400, 'amount must be a positive whole number');
  if (fromId === toId) throw new WalletError(400, 'Cannot transfer to the same wallet');

  const from = walletOrFail(fromId);
  const to = walletOrFail(toId);
  activeOrFail(from);
  activeOrFail(to);
  if (from.balance < amount) throw new WalletError(409, 'Insufficient funds');

  store.record(from, 'transfer_out', amount, at, to.id);
  store.record(to, 'transfer_in', amount, at, from.id);
  return { from, to, amount };
};

module.exports = { transfer };
