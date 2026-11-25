package com.wallet.store;

import com.wallet.model.Transaction;
import com.wallet.model.Wallet;
import com.wallet.model.WalletData;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Component;

/**
 * An in-memory store standing in for the wallet database. reset() loads a data set (seed.json when the app starts;
 * the tests load their own).
 */
@Component
public class WalletStore {
    private Map<String, Wallet> wallets = new LinkedHashMap<>();
    private List<Transaction> transactions = new ArrayList<>();
    private int nextTx = 1;

    public synchronized void reset(WalletData data) {
        wallets = new LinkedHashMap<>();
        transactions = new ArrayList<>();
        if (data != null) {
            if (data.wallets() != null) data.wallets().forEach(w -> wallets.put(w.id(), w));
            if (data.transactions() != null) transactions.addAll(data.transactions());
        }
        nextTx = transactions.size() + 1;
    }

    public synchronized Wallet getWallet(String id) {
        return id == null ? null : wallets.get(id);
    }

    public synchronized List<Transaction> transactionsOf(String walletId) {
        return transactions.stream().filter(t -> t.walletId().equals(walletId)).toList();
    }

    /** Changes a wallet's balance and records the transaction. */
    public synchronized Transaction record(String walletId, String type, long amount, String at, String counterparty) {
        Wallet wallet = wallets.get(walletId);
        boolean in = "deposit".equals(type) || "transfer_in".equals(type);
        Wallet updated = wallet.withBalance(wallet.balance() + (in ? amount : -amount));
        wallets.put(walletId, updated);
        Transaction tx = new Transaction("TX" + nextTx++, walletId, type, amount, updated.balance(), counterparty, at);
        transactions.add(tx);
        return tx;
    }
}
