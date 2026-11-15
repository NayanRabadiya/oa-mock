package com.library;

import com.fasterxml.jackson.databind.JsonNode;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletResponse;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

/** The integrated tests for the library loans API. Run them with:  mvn test */
class LoanTests extends LibraryTestSupport {
    @Test
    void borrowingAndReturningABookChangesTheCopiesOnTheShelf() throws Exception {
        assertEquals(2, available("B1"));
        MockHttpServletResponse res = borrow("M1", "B1");
        assertEquals(201, res.getStatus(), res.getContentAsString());
        JsonNode loan = json(res);
        assertEquals("M1", loan.path("memberId").asText());
        assertEquals("B1", loan.path("bookId").asText());
        assertEquals("2026-11-01", loan.path("borrowedAt").asText());
        assertTrue(loan.path("returnedAt").isNull(), loan.toString());
        assertEquals(1, available("B1"));
        assertEquals(200, giveBack(loan.path("id").asText(), "2026-11-10").getStatus());
        assertEquals(2, available("B1"));
    }

    @Test
    void aMemberCanHaveAtMost3BooksOut() throws Exception {
        for (String book : new String[] {"B1", "B2", "B3"}) {
            assertEquals(201, borrow("M1", book).getStatus());
        }
        MockHttpServletResponse fourth = borrow("M1", "B3");
        assertEquals(409, fourth.getStatus());
        assertEquals("Loan limit reached", message(fourth));
        assertEquals(201, borrow("M2", "B3").getStatus());
    }

    @Test
    void lateFeesStartAfterThe14DayLoanPeriod() throws Exception {
        String onTime = json(borrow("M1", "B1", "2026-11-01")).path("id").asText();
        JsonNode first = json(giveBack(onTime, "2026-11-15"));                 // day 14: on time
        assertEquals(0, first.path("daysLate").asInt(), first.toString());
        assertEquals(0, first.path("fee").asInt(), first.toString());
        String late = json(borrow("M1", "B1", "2026-11-01")).path("id").asText();
        JsonNode second = json(giveBack(late, "2026-11-18"));
        assertEquals(3, second.path("daysLate").asInt(), second.toString());
        assertEquals(30, second.path("fee").asInt(), second.toString());
    }

    @Test
    void aLoanCanBeReturnedOnlyOnce() throws Exception {
        String loan = json(borrow("M1", "B1")).path("id").asText();
        assertEquals(200, giveBack(loan, "2026-11-05").getStatus());
        MockHttpServletResponse again = giveBack(loan, "2026-11-06");
        assertEquals(409, again.getStatus());
        assertEquals("Loan already returned", message(again));
    }
}
