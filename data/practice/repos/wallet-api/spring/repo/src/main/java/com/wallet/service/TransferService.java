package com.wallet.service;

import com.wallet.model.Wallet;
import com.wallet.store.WalletStore;
import java.util.LinkedHashMap;
import java.util.Map;
import org.springframework.stereotype.Service;

@Service
public class TransferService {
    private final WalletStore store;
    private final WalletService wallets;

    public TransferService(WalletStore store, WalletService wallets) {
        this.store = store;
        this.wallets = wallets;
    }

    /**
     * Moves money between two wallets. Either both sides change or neither does: every check runs before any
     * balance changes.
     */
    public Map<String, Object> transfer(String fromId, String toId, Object rawAmount, String at) {
        if (fromId == null || toId == null || rawAmount == null) {
            throw new WalletException(400, "from, to and amount are required");
        }
        long amount = WalletService.amountOf(rawAmount);
        if (fromId.equals(toId)) {
            throw new WalletException(400, "Cannot transfer to the same wallet");
        }

        Wallet from = wallets.walletOrFail(fromId);
        wallets.activeOrFail(from);
        if (from.balance() < amount) {
            throw new WalletException(409, "Insufficient funds");
        }
        store.record(from.id(), "transfer_out", amount, at, toId);

        Wallet to = wallets.walletOrFail(toId);
        wallets.activeOrFail(to);
        store.record(to.id(), "transfer_in", amount, at, from.id());

        Map<String, Object> out = new LinkedHashMap<>();
        out.put("from", store.getWallet(fromId));
        out.put("to", store.getWallet(toId));
        out.put("amount", amount);
        return out;
    }
}
