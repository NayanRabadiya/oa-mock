package com.wallet.service;

import com.wallet.model.Transaction;
import com.wallet.model.Wallet;
import com.wallet.store.WalletStore;
import com.wallet.util.Times;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Service;

@Service
public class WalletService {
    /** Newest first (then the later transaction first). */
    private static final Comparator<Transaction> NEWEST_FIRST =
            Comparator.<Transaction, java.time.Instant>comparing(t -> Times.parse(t.at())).thenComparingInt(Transaction::number).reversed();

    private final WalletStore store;

    public WalletService(WalletStore store) {
        this.store = store;
    }

    /** A positive whole number sent as a JSON number. */
    public static long amountOf(Object value) {
        if ((value instanceof Integer || value instanceof Long) && ((Number) value).longValue() > 0) {
            return ((Number) value).longValue();
        }
        throw new WalletException(400, "amount must be a positive whole number");
    }

    public Wallet walletOrFail(String id) {
        Wallet wallet = store.getWallet(id);
        if (wallet == null) {
            throw new WalletException(404, "Wallet not found");
        }
        return wallet;
    }

    public void activeOrFail(Wallet wallet) {
        if (!wallet.active()) {
            throw new WalletException(409, "Wallet is frozen");
        }
    }

    public Map<String, Object> deposit(String id, Object rawAmount, String at) {
        long amount = amountOf(rawAmount);
        Wallet wallet = walletOrFail(id);
        activeOrFail(wallet);
        Transaction tx = store.record(id, "deposit", amount, at, null);
        return result(store.getWallet(id), tx);
    }

    public Map<String, Object> withdraw(String id, Object rawAmount, String at) {
        long amount = amountOf(rawAmount);
        Wallet wallet = walletOrFail(id);
        activeOrFail(wallet);
        if (wallet.balance() < amount) {
            throw new WalletException(409, "Insufficient funds");
        }
        Transaction tx = store.record(id, "withdrawal", amount, at, null);
        return result(store.getWallet(id), tx);
    }

    public List<Transaction> history(String id, String type, int limit) {
        walletOrFail(id);
        return store.transactionsOf(id).stream()
                .filter(t -> type == null || type.equals(t.type()))
                .sorted(NEWEST_FIRST)
                .limit(limit)
                .toList();
    }

    private static Map<String, Object> result(Wallet wallet, Transaction tx) {
        Map<String, Object> out = new LinkedHashMap<>();
        out.put("wallet", wallet);
        out.put("transaction", tx);
        return out;
    }
}
