package com.returns;

import java.util.List;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

/** The integrated tests for the return/risk service. Run them with:  mvn test */
class ReturnEvaluationTests extends ReturnsTestSupport {
    @Test
    void acceptsAReturnOnTheLastDayOfTheWindow() throws Exception {
        order("O-1", "C5", "2026-10-16", "Electronics", 40, 1);   // 30 days before 2026-11-15
        order("O-2", "C5", "2026-10-15", "Electronics", 40, 1);   // 31 days before
        assertEvaluation(evaluate("O-1"), "AUTO_APPROVE", 0, List.of());
        assertEvaluation(evaluate("O-2"), "REJECT", null, List.of("RETURN_WINDOW_EXPIRED"));
    }

    @Test
    void matchesCategoriesWhateverTheirCase() throws Exception {
        order("O-1", "C5", "2026-11-01", "Electronics", 40, 1);
        order("O-2", "C5", "2026-11-01", "HOME & KITCHEN", 40, 1);
        order("O-3", "C5", "2026-11-01", "Grocery", 40, 1);
        assertEquals("AUTO_APPROVE", evaluate("O-1").path("decision").asText());
        assertEquals("AUTO_APPROVE", evaluate("O-2").path("decision").asText());
        assertEvaluation(evaluate("O-3"), "REJECT", null, List.of("NON_RETURNABLE_CATEGORY"));
    }

    @Test
    void countsReturnsAcrossEveryLinkedAccount() throws Exception {
        pastReturn("C3", "APPROVED", 100, "2026-10-01");           // C3 is linked to C1 through C2
        pastReturn("C3", "APPROVED", 100, "2026-11-02");
        order("O-1", "C1", 40);
        assertEvaluation(evaluate("O-1"), "AUTO_APPROVE", 20, List.of("RETURN_FREQUENCY"));
    }

    @Test
    void onlyApprovedReturnsCountTowardTheHistory() throws Exception {
        pastReturn("C5", "APPROVED", 100, "2026-10-20");
        pastReturn("C5", "REJECTED", 100, "2026-10-20");
        pastReturn("C5", "REJECTED", 100, "2026-10-20");
        pastReturn("C5", "PENDING_REVIEW", 100, "2026-10-20");
        order("O-1", "C5", 40);
        assertEvaluation(evaluate("O-1"), null, 10, List.of("RETURN_FREQUENCY"));
    }

    @Test
    void scoresTheValueOfTheReturnAsPriceTimesQuantity() throws Exception {
        order("O-1", "C5", "2026-11-01", "Electronics", 120, 2);  // 240
        order("O-2", "C3", "2026-11-01", "Electronics", 30, 2);   // 60 (another customer: an approval goes into the history)
        assertEvaluation(evaluate("O-1"), null, 15, List.of("ORDER_VALUE_ELEVATED"));
        assertEvaluation(evaluate("O-2"), null, 5, List.of("ORDER_VALUE_MODERATE"));
    }

    @Test
    void decidesAtTheScoreThresholds() throws Exception {
        pastReturn("C1", "APPROVED", 1200, "2026-10-20");          // +10 history, +15 refunded over 1000
        order("O-1", "C1", 600);                                    // +25 value, +20 changed mind = 70
        assertEvaluation(evaluate("O-1", "CHANGED_MIND"), "REJECT", 70, List.of("REASON_DISCRETIONARY",
                "ORDER_VALUE_HIGH", "RETURN_FREQUENCY", "REFUND_TOTAL_HIGH", "HIGH_RISK"));

        pastReturn("C5", "APPROVED", 20, "2026-10-20");            // +10 history
        order("O-2", "C5", 40);                                     // +20 changed mind = 30
        assertEvaluation(evaluate("O-2", "CHANGED_MIND"), "MANUAL_REVIEW", 30, null);

        order("O-3", "C9", 300);                                    // new account +10, +15 value = 25
        assertEvaluation(evaluate("O-3"), "AUTO_APPROVE", 25, null);
    }
}
