package com.wallet.model;

import java.util.List;

/** A data set for the store: what src/main/resources/seed.json holds. */
public record WalletData(List<Wallet> wallets, List<Transaction> transactions) {}
