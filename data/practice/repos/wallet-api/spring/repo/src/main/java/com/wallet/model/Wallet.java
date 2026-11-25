package com.wallet.model;

/** A wallet. Balances are whole rupees; status is active or frozen. */
public record Wallet(String id, String owner, long balance, String status) {
    public Wallet withBalance(long newBalance) {
        return new Wallet(id, owner, newBalance, status);
    }

    public boolean active() {
        return "active".equals(status);
    }
}
