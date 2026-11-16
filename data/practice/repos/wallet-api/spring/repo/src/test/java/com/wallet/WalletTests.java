package com.wallet;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletResponse;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

/** The integrated tests for the wallet API. Run them with:  mvn test */
class WalletTests extends WalletTestSupport {
    @Test
    void aDepositAddsToTheBalance() throws Exception {
        MockHttpServletResponse res = deposit("W1", 250);
        assertEquals(200, res.getStatus(), res.getContentAsString());
        JsonNode w = json(res).path("wallet"), tx = json(res).path("transaction");
        assertEquals("W1", w.path("id").asText());
        assertEquals("Asha", w.path("owner").asText());
        assertEquals(1250, w.path("balance").asLong());
        assertEquals("active", w.path("status").asText());
        assertEquals("TX1", tx.path("id").asText());
        assertEquals("W1", tx.path("walletId").asText());
        assertEquals("deposit", tx.path("type").asText());
        assertEquals(250, tx.path("amount").asLong());
        assertEquals(1250, tx.path("balanceAfter").asLong());
        assertTrue(tx.path("counterparty").isNull(), tx.toString());
        assertEquals("2026-11-15T09:00:00Z", tx.path("at").asText());
    }

    @Test
    void aTransferMovesMoneyBetweenWallets() throws Exception {
        MockHttpServletResponse res = send("W1", "W2", 300);
        assertEquals(201, res.getStatus(), res.getContentAsString());
        JsonNode body = json(res);
        assertEquals(300, body.path("amount").asLong());
        assertEquals(700, body.path("from").path("balance").asLong());
        assertEquals(500, body.path("to").path("balance").asLong());
        assertEquals(500, balance(wallet("W2")));
    }

    @Test
    void aFailedTransferChangesNothing() throws Exception {
        MockHttpServletResponse res = send("W1", "W404", 300);
        assertEquals(404, res.getStatus());
        assertEquals("Wallet not found", message(res));
        assertEquals(1000, balance(wallet("W1")));
        assertEquals(List.of(), each(history("W1"), "id"));
    }

    @Test
    void listsAWalletsTransactionsNewestFirst() throws Exception {
        deposit("W1", 100, "2026-11-15T08:00:00Z");
        deposit("W1", 50, "2026-11-15T11:00:00Z");
        deposit("W2", 70, "2026-11-15T09:00:00Z");
        MockHttpServletResponse res = history("W1");
        assertEquals(200, res.getStatus(), res.getContentAsString());
        assertEquals(List.of("TX2", "TX1"), each(res, "id"));
        assertEquals(List.of("50", "100"), each(res, "amount"));
        assertEquals(List.of("1150", "1100"), each(res, "balanceAfter"));
    }

    @Test
    void filtersTransactionsByType() throws Exception {
        deposit("W2", 100, "2026-11-15T08:00:00Z");
        send("W2", "W1", 50, "2026-11-15T09:00:00Z");
        send("W1", "W2", 20, "2026-11-15T10:00:00Z");
        MockHttpServletResponse res = history("W2", "?type=transfer_out");
        assertEquals(200, res.getStatus(), res.getContentAsString());
        assertEquals(List.of("transfer_out"), each(res, "type"));
        assertEquals(List.of("50"), each(res, "amount"));
        assertEquals(List.of("W1"), each(res, "counterparty"));
        assertEquals(List.of("20"), each(history("W2", "?type=transfer_in"), "amount"));
    }
}
