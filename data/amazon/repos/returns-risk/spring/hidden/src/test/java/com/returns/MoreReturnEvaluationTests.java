package com.returns;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletResponse;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;

/** More integrated tests (hidden in the test: they run when you submit). */
class MoreReturnEvaluationTests extends ReturnsTestSupport {
    private static void assertError(MockHttpServletResponse res, int status, String message) throws Exception {
        assertEquals(status, res.getStatus(), res.getContentAsString());
        if (message != null) assertEquals(message, json(res).path("message").asText());
    }

    @Test
    void validatesTheRequest() throws Exception {
        order("O-1", "C5", 40);
        assertError(post(Map.of("orderId", "O-1")), 400, "orderId, itemId and reason are required");
        assertError(evaluateResponse("O-1", "BORED"), 400, "Invalid return reason");
        assertError(evaluateResponse("O-1", "DAMAGED", "requestedAt", "15/11/2026"), 400, null);
        assertError(evaluateResponse("O-404", "DAMAGED"), 404, "Order not found");
        assertError(evaluateResponse("O-1", "DAMAGED", "itemId", "I-9"), 404, "Item not found in order");
    }

    @Test
    void rejectsOrdersThatHaveNotBeenDelivered() throws Exception {
        order("O-1", "C5", "SHIPPED", null, "Electronics", 40, 1);
        assertEvaluation(evaluate("O-1"), "REJECT", 0, List.of("NOT_DELIVERED"));
    }

    @Test
    void anItemCanHaveOnlyOneOpenReturn() throws Exception {
        order("O-1", "C5", 40);
        assertEquals("AUTO_APPROVE", evaluate("O-1").path("decision").asText());
        assertEvaluation(evaluate("O-1"), "REJECT", null, List.of("ALREADY_RETURNED"));
        order("O-2", "C5", 40);
        pastReturn("C5", "REJECTED", 100, "2026-10-20", "O-2");     // a rejected return doesn't block a new one
        assertFalse(strings(evaluate("O-2").path("reasons")).contains("ALREADY_RETURNED"));
    }

    @Test
    void capsTheScoreAt100() throws Exception {
        for (int i = 0; i < 5; i++) {
            pastReturn("C9", "APPROVED", 300, "2026-11-0" + (i + 2));
        }
        order("O-1", "C9", 800);
        assertEvaluation(evaluate("O-1", "NO_LONGER_NEEDED"), "REJECT", 100, List.of("REASON_DISCRETIONARY",
                "ORDER_VALUE_HIGH", "RETURN_FREQUENCY", "REFUND_TOTAL_HIGH", "NEW_ACCOUNT", "HIGH_RISK"));
    }

    @Test
    void historyCoversThe90DaysBeforeTheRequest() throws Exception {
        pastReturn("C5", "APPROVED", 100, "2026-08-17");           // 90 days before: counts
        pastReturn("C5", "APPROVED", 100, "2026-08-16");           // 91 days before: doesn't
        pastReturn("C5", "APPROVED", 100, "2026-11-20");           // after the request: doesn't
        order("O-1", "C5", 40);
        assertEvaluation(evaluate("O-1"), null, 10, List.of("RETURN_FREQUENCY"));
    }

    @Test
    void theRefundTotalMustBeMoreThan1000() throws Exception {
        pastReturn("C5", "APPROVED", 500, "2026-10-20");
        pastReturn("C5", "APPROVED", 500, "2026-10-20");
        order("O-1", "C5", 40);
        assertEvaluation(evaluate("O-1"), null, null, List.of("RETURN_FREQUENCY"));
        pastReturn("C5", "APPROVED", 0.01, "2026-10-20");
        assertEvaluation(evaluate("O-1"), null, null, List.of("RETURN_FREQUENCY", "REFUND_TOTAL_HIGH"));
    }

    @Test
    void everyReasonComesWithItsMessage() throws Exception {
        order("O-1", "C9", 75);
        JsonNode res = evaluate("O-1", "NOT_AS_DESCRIBED");
        assertEvaluation(res, "AUTO_APPROVE", 25, List.of("REASON_NOT_AS_DESCRIBED", "ORDER_VALUE_MODERATE", "NEW_ACCOUNT"));
        assertEquals(List.of("The customer says the item is not as described", "The return is worth 50 or more",
                "The account is less than 30 days old"), strings(res.path("messages")));
    }

    @Test
    void evaluationsAreRecordedInTheHistory() throws Exception {
        order("O-1", "C5", "2026-11-01", "Electronics", 45, 2);
        order("O-2", "C5", 40);
        JsonNode first = evaluate("O-1");
        assertEquals("AUTO_APPROVE", first.path("decision").asText());
        MockHttpServletResponse listedRes = get("/api/returns/customer/C5");
        assertEquals(200, listedRes.getStatus());
        JsonNode listed = json(listedRes);
        assertEquals(1, listed.size());
        JsonNode saved = listed.get(0);
        assertEquals(first.path("returnId").asText(), saved.path("id").asText());
        assertEquals("O-1", saved.path("orderId").asText());
        assertEquals("APPROVED", saved.path("status").asText());
        assertEquals(90.0, saved.path("amount").asDouble());
        assertEquals("2026-11-15", saved.path("date").asText());
        assertEvaluation(evaluate("O-2"), null, 10, List.of("RETURN_FREQUENCY"));
        assertEquals(404, get("/api/returns/customer/C404").getStatus());
    }
}
