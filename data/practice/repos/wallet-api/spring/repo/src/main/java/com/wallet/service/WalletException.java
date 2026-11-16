package com.wallet.service;

/** An error with the HTTP status the API answers with. */
public class WalletException extends RuntimeException {
    private final int status;

    public WalletException(int status, String message) {
        super(message);
        this.status = status;
    }

    public int status() {
        return status;
    }
}
