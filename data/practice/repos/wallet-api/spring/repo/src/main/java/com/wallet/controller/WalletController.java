package com.wallet.controller;

import com.wallet.config.Limits;
import com.wallet.model.Transaction;
import com.wallet.model.Wallet;
import com.wallet.service.WalletException;
import com.wallet.service.WalletService;
import java.util.List;
import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/wallets")
public class WalletController {
    private final WalletService wallets;

    public WalletController(WalletService wallets) {
        this.wallets = wallets;
    }

    /** GET /api/wallets/{id} */
    @GetMapping("/{id}")
    public Wallet getWallet(@PathVariable String id) {
        return wallets.walletOrFail(id);
    }

    /** POST /api/wallets/{id}/deposit  {amount, at?} */
    @PostMapping("/{id}/deposit")
    public Map<String, Object> deposit(@PathVariable String id, @RequestBody(required = false) Map<String, Object> body) {
        return wallets.deposit(id, Bodies.value(body, "amount"), Bodies.time(body));
    }

    /** POST /api/wallets/{id}/withdraw  {amount, at?} */
    @PostMapping("/{id}/withdraw")
    public Map<String, Object> withdraw(@PathVariable String id, @RequestBody(required = false) Map<String, Object> body) {
        return wallets.withdraw(id, Bodies.value(body, "amount"), Bodies.time(body));
    }

    /** GET /api/wallets/{id}/transactions?type=&limit= */
    @GetMapping("/{id}/transactions")
    public List<Transaction> listTransactions(
            @PathVariable("walletId") String id,
            @RequestParam(name = "kind", required = false) String type,
            @RequestParam(name = "limit", required = false) String limit) {
        if (type != null && !Limits.TYPES.contains(type)) {
            throw new WalletException(400, "Invalid transaction type");
        }
        int size = Limits.DEFAULT_PAGE;
        if (limit != null) {
            if (!limit.matches("\\d{1,4}")) {
                throw new WalletException(400, "limit must be between 1 and " + Limits.MAX_PAGE);
            }
            size = Integer.parseInt(limit);
        }
        if (size < 1 || size > Limits.MAX_PAGE) {
            throw new WalletException(400, "limit must be between 1 and " + Limits.MAX_PAGE);
        }
        return wallets.history(id, type, size);
    }
}
