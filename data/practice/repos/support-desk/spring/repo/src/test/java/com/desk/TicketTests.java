package com.desk;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletResponse;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

/** The integrated tests for the support desk API. Run them with:  mvn test */
class TicketTests extends DeskTestSupport {
    @Test
    void creatingATicketOpensIt() throws Exception {
        MockHttpServletResponse res = create("high");
        assertEquals(201, res.getStatus(), res.getContentAsString());
        JsonNode t = json(res);
        assertEquals("T1", t.path("id").asText());
        assertEquals("Help", t.path("title").asText());
        assertEquals("acme", t.path("customer").asText());
        assertEquals("high", t.path("priority").asText());
        assertEquals("open", t.path("status").asText());
        assertEquals("2026-11-15T09:00:00Z", t.path("createdAt").asText());
        assertTrue(t.path("assigneeId").isNull(), t.toString());
        assertTrue(t.path("resolvedAt").isNull(), t.toString());
    }

    @Test
    void ticketsAreListedByPriorityOldestFirst() throws Exception {
        create("low", "2026-11-15T08:00:00Z");
        create("high", "2026-11-15T10:00:00Z");
        create("urgent", "2026-11-15T11:00:00Z");
        create("high", "2026-11-15T09:00:00Z");
        assertEquals(List.of("T3", "T4", "T2", "T1"), ids(get("/api/tickets")));
    }

    @Test
    void anAgentCannotTakeMoreTicketsThanTheirLimit() throws Exception {
        for (int i = 0; i < 3; i++) create("medium");
        assertEquals("in_progress", json(assign("T1", "A1")).path("status").asText());
        assertEquals(200, assign("T2", "A1").getStatus());
        MockHttpServletResponse third = assign("T3", "A1");
        assertEquals(409, third.getStatus());
        assertEquals("Agent has too many open tickets", message(third));
        assertEquals(200, assign("T3", "A2").getStatus());
    }

    @Test
    void ticketsMoveThroughTheWorkflowInOrder() throws Exception {
        create("low");
        assertEquals(409, move("T1", "resolved").getStatus());
        assertEquals(200, move("T1", "in_progress").getStatus());
        MockHttpServletResponse early = move("T1", "closed");
        assertEquals(409, early.getStatus());
        assertEquals("Cannot move a ticket from in_progress to closed", message(early));
        assertEquals(200, move("T1", "resolved").getStatus());
        assertEquals("closed", json(move("T1", "closed")).path("status").asText());
    }

    @Test
    void aTicketIsOverdueOnlyAfterItsSLA() throws Exception {
        create("high", "2026-11-14T10:00:00Z");      // 23 hours before the check
        create("high", "2026-11-14T08:00:00Z");      // 25 hours before
        create("urgent", "2026-11-15T05:30:00Z");    // 3.5 hours before
        MockHttpServletResponse res = get("/api/tickets/overdue?now=2026-11-15T09:00:00Z");
        assertEquals(200, res.getStatus());
        assertEquals(List.of("T2"), ids(res));
    }
}
