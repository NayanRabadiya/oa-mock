package com.library;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletResponse;

import static org.junit.jupiter.api.Assertions.assertEquals;

/** More integrated tests (hidden in the test: they run when you submit). */
class MoreLoanTests extends LibraryTestSupport {
    @Test
    void validatesTheRequest() throws Exception {
        assertEquals("memberId and bookId are required", message(post("/api/loans", Map.of("memberId", "M1"))));
        assertEquals(404, borrow("M9", "B1").getStatus());
        assertEquals("Book not found", message(borrow("M1", "B9")));
        assertEquals(400, borrow("M1", "B1", "1/11/2026").getStatus());
        assertEquals("Loan not found", message(giveBack("L99", "2026-11-05")));
    }

    @Test
    void aBookWithEveryCopyOutCannotBeBorrowed() throws Exception {
        assertEquals(201, borrow("M1", "B2").getStatus());
        MockHttpServletResponse none = borrow("M2", "B2");
        assertEquals(409, none.getStatus());
        assertEquals("No copies available", message(none));
    }

    @Test
    void theFeeForOneLoanIsAtMost200() throws Exception {
        String loan = json(borrow("M1", "B1", "2026-10-01")).path("id").asText();
        JsonNode res = json(giveBack(loan, "2026-11-15"));
        assertEquals(31, res.path("daysLate").asInt(), res.toString());
        assertEquals(200, res.path("fee").asInt(), res.toString());
    }
}
