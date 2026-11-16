package com.desk.controller;

import com.desk.config.DeskRules;
import com.desk.model.Agent;
import com.desk.model.Ticket;
import com.desk.service.AssignmentService;
import com.desk.service.SlaService;
import com.desk.service.TicketService;
import com.desk.service.WorkflowService;
import com.desk.store.DeskStore;
import com.desk.util.Times;
import java.util.List;
import java.util.Map;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/tickets")
public class TicketController {
    private final DeskStore store;
    private final TicketService tickets;
    private final AssignmentService assignment;
    private final WorkflowService workflow;
    private final SlaService sla;

    public TicketController(DeskStore store, TicketService tickets, AssignmentService assignment, WorkflowService workflow,
                            SlaService sla) {
        this.store = store;
        this.tickets = tickets;
        this.assignment = assignment;
        this.workflow = workflow;
        this.sla = sla;
    }

    private static ResponseEntity<Map<String, String>> fail(int status, String message) {
        return ResponseEntity.status(status).body(Map.of("message", message));
    }

    private static String text(Map<String, Object> body, String key) {
        Object value = body == null ? null : body.get(key);
        return value == null || value.toString().isEmpty() ? null : value.toString();
    }

    /** GET /api/tickets?status=&priority=&assigneeId= */
    @GetMapping
    public List<Ticket> listTickets(@RequestParam(required = false) String status,
                                    @RequestParam(required = false) String priority,
                                    @RequestParam(required = false) String assigneeId) {
        return tickets.sortTickets(tickets.filterTickets(store.allTickets(), status, priority, assigneeId));
    }

    /** POST /api/tickets  {title, customer, priority, createdAt?} */
    @PostMapping
    public ResponseEntity<?> createTicket(@RequestBody(required = false) Map<String, Object> body) {
        String title = text(body, "title");
        String customer = text(body, "customer");
        String priority = text(body, "priority");
        String createdAt = text(body, "createdAt") == null ? Times.now() : text(body, "createdAt");
        if (title == null || customer == null || priority == null) {
            return fail(400, "title, customer and priority are required");
        }
        if (!DeskRules.PRIORITIES.contains(priority)) {
            return fail(400, "Invalid priority");
        }
        if (!Times.isIsoTime(createdAt)) {
            return fail(400, "createdAt must be a time like 2026-11-15T09:30:00Z");
        }
        Ticket saved = store.addTicket(new Ticket(null, title, customer, priority, "open", null, createdAt, null));
        return ResponseEntity.status(201).body(saved);
    }

    /** POST /api/tickets/{id}/assign  {agentId} */
    @PostMapping("/{id}/assign")
    public ResponseEntity<?> assignTicket(@PathVariable String id, @RequestBody(required = false) Map<String, Object> body) {
        Ticket ticket = store.getTicket(id);
        if (ticket == null) {
            return fail(404, "Ticket not found");
        }
        Agent agent = store.getAgent(text(body, "agentId"));
        if (agent == null) {
            return fail(404, "Agent not found");
        }
        if (!List.of("open", "in_progress").contains(ticket.status())) {
            return fail(409, "Only open or in-progress tickets can be assigned");
        }
        if (!assignment.canTake(agent, ticket)) {
            return fail(409, "Agent has too many open tickets");
        }
        String status = "open".equals(ticket.status()) ? "in_progress" : ticket.status();
        return ResponseEntity.ok(store.save(ticket.withAssignee(agent.id(), status)));
    }

    /** POST /api/tickets/{id}/status  {status, at?} */
    @PostMapping("/{id}/status")
    public ResponseEntity<?> changeStatus(@PathVariable String id, @RequestBody(required = false) Map<String, Object> body) {
        Ticket ticket = store.getTicket(id);
        if (ticket == null) {
            return fail(404, "Ticket not found");
        }
        String status = text(body, "status");
        String at = text(body, "at") == null ? Times.now() : text(body, "at");
        if (status == null || !DeskRules.STATUSES.contains(status)) {
            return fail(400, "Invalid status");
        }
        if (!workflow.canMove(ticket.status(), status)) {
            return fail(409, "Cannot move a ticket from " + ticket.status() + " to " + status);
        }
        String resolvedAt = "resolved".equals(status) ? at : "in_progress".equals(status) ? null : ticket.resolvedAt();
        return ResponseEntity.ok(store.save(ticket.withStatus(status, resolvedAt)));
    }

    /** GET /api/tickets/overdue?now= */
    @GetMapping("/overdue")
    public ResponseEntity<?> overdueTickets(@RequestParam(required = false) String now) {
        String at = now == null || now.isEmpty() ? Times.now() : now;
        if (!Times.isIsoTime(at)) {
            return fail(400, "now must be a time like 2026-11-15T09:30:00Z");
        }
        return ResponseEntity.ok(tickets.sortTickets(store.allTickets().stream().filter(t -> sla.isOverdue(t, at)).toList()));
    }
}
