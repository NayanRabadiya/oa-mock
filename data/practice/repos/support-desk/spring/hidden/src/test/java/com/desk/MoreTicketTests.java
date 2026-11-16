package com.desk;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

/** More integrated tests (hidden in the test: they run when you submit). */
class MoreTicketTests extends DeskTestSupport {
    @Test
    void validatesTheRequest() throws Exception {
        assertEquals("title, customer and priority are required", message(post("/api/tickets", Map.of("title", "x"))));
        assertEquals("Invalid priority", message(create("critical")));
        assertEquals(400, create("low", "15/11/2026").getStatus());
        assertEquals("Ticket not found", message(assign("T9", "A1")));
        create("low");
        assertEquals("Agent not found", message(assign("T1", "A9")));
        assertEquals("Invalid status", message(move("T1", "done")));
    }

    @Test
    void filtersByStatusPriorityAndAssignee() throws Exception {
        create("low");
        create("high");
        create("high");
        assign("T2", "A1");
        assertEquals(List.of("T2", "T3"), ids(get("/api/tickets?priority=high")));
        assertEquals(List.of("T3", "T1"), ids(get("/api/tickets?status=open")));
        assertEquals(List.of("T2"), ids(get("/api/tickets?assigneeId=A1&status=in_progress")));
        assertEquals(List.of(), ids(get("/api/tickets?assigneeId=A2")));
    }

    @Test
    void resolvingRecordsWhenReopeningClearsIt() throws Exception {
        create("medium");
        move("T1", "in_progress");
        assertEquals("2026-11-15T13:00:00Z", json(move("T1", "resolved", "2026-11-15T13:00:00Z")).path("resolvedAt").asText());
        JsonNode reopened = json(move("T1", "in_progress"));
        assertEquals("in_progress", reopened.path("status").asText());
        assertTrue(reopened.path("resolvedAt").isNull(), reopened.toString());
        move("T1", "resolved");
        move("T1", "closed");
        assertEquals(409, move("T1", "in_progress").getStatus());
        assertEquals("Only open or in-progress tickets can be assigned", message(assign("T1", "A1")));
    }

    @Test
    void finishedTicketsAreNeverOverdueAndDoNotCountTowardAnAgentLimit() throws Exception {
        for (int i = 0; i < 3; i++) create("urgent", "2026-11-10T00:00:00Z");
        assign("T1", "A1");
        assign("T2", "A1");
        move("T1", "resolved");
        assertEquals(List.of("T2", "T3"), ids(get("/api/tickets/overdue?now=2026-11-15T09:00:00Z")));
        assertEquals(200, assign("T3", "A1").getStatus());
    }
}
