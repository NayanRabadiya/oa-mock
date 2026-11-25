package com.wallet;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

/** More integrated tests (hidden in the test: they run when you submit). */
class MoreWalletTests extends WalletTestSupport {
    @Test
    void validatesAmountsAndWallets() throws Exception {
        assertEquals("amount must be a positive whole number", message(deposit("W1", 0)));
        assertEquals(400, deposit("W1", 2.5).getStatus());
        assertEquals(400, deposit("W1", "10").getStatus());
        assertEquals("Wallet not found", message(deposit("W9", 10)));
        assertEquals(404, wallet("W9").getStatus());
        assertEquals("from, to and amount are required", message(post("/api/transfers", Map.of("from", "W1"))));
        assertEquals("Cannot transfer to the same wallet", message(send("W1", "W1", 10)));
        assertEquals("Invalid transaction type", message(history("W1", "?type=refund")));
        assertEquals(400, history("W1", "?limit=0").getStatus());
    }

    @Test
    void cannotSpendMoreThanTheBalance() throws Exception {
        assertEquals("Insufficient funds", message(withdraw("W2", 201)));
        assertEquals(409, send("W2", "W1", 201).getStatus());
        JsonNode all = json(withdraw("W2", 200));
        assertEquals(0, all.path("wallet").path("balance").asLong());
        assertEquals("withdrawal", all.path("transaction").path("type").asText());
        assertEquals(200, all.path("transaction").path("amount").asLong());
        assertEquals(0, all.path("transaction").path("balanceAfter").asLong());
    }

    @Test
    void frozenWalletsCannotSendOrReceive() throws Exception {
        assertEquals("Wallet is frozen", message(send("W3", "W1", 10)));
        assertEquals(409, send("W1", "W3", 10).getStatus());
        assertEquals(409, deposit("W3", 10).getStatus());
        assertEquals(1000, balance(wallet("W1")));
        assertEquals(500, balance(wallet("W3")));
    }

    @Test
    void limitCapsTheTransactionList() throws Exception {
        for (int i = 1; i <= 25; i++) deposit("W1", i, String.format("2026-11-15T09:%02d:00Z", i));
        assertEquals(20, each(history("W1"), "id").size());
        assertEquals(List.of("25", "24"), each(history("W1", "?limit=2"), "amount"));
        assertEquals(List.of("25", "24", "23"), each(history("W1", "?type=deposit&limit=3"), "amount"));
    }
}
