// An error with the HTTP status the API answers with.
class WalletError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

module.exports = { WalletError };
