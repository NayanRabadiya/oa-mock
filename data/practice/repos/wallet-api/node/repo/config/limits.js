// Limits of the wallet API.
module.exports = {
  DEFAULT_PAGE: 20,      // transactions returned when no limit is given
  MAX_PAGE: 100,         // the most a client can ask for
  TYPES: ['deposit', 'withdrawal', 'transfer_in', 'transfer_out'],
};
