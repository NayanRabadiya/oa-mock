package com.wallet.model;

/** One entry of a wallet's history; counterparty is the other wallet of a transfer, else null. */
public record Transaction(String id, String walletId, String type, long amount, long balanceAfter, String counterparty,
                          String at) {
    public int number() {
        return Integer.parseInt(id.substring(2));
    }
}
