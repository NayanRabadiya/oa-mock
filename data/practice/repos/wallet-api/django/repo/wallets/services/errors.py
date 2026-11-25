class WalletError(Exception):
    """An error with the HTTP status the API answers with."""

    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message
