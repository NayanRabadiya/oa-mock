package com.desk.service;

import com.desk.config.DeskRules;
import com.desk.model.Ticket;
import com.desk.util.Times;
import java.util.Comparator;
import java.util.List;
import java.util.Objects;
import org.springframework.stereotype.Service;

@Service
public class TicketService {
    /** Most urgent first; tickets of the same priority oldest first (then by id). */
    private static final Comparator<Ticket> QUEUE_ORDER =
            Comparator.<Ticket>comparingInt(t -> DeskRules.PRIORITIES.indexOf(t.priority()))
                    .thenComparing(t -> Times.parse(t.createdAt()))
                    .thenComparingInt(Ticket::number);

    public List<Ticket> sortTickets(List<Ticket> tickets) {
        return tickets.stream().sorted(QUEUE_ORDER).toList();
    }

    /** Keeps the tickets that match every filter given (null means any). */
    public List<Ticket> filterTickets(List<Ticket> tickets, String status, String priority, String assigneeId) {
        return tickets.stream()
                .filter(t -> status == null || status.equals(t.status()))
                .filter(t -> priority == null || priority.equals(t.priority()))
                .filter(t -> assigneeId == null || Objects.equals(assigneeId, t.assigneeId()))
                .toList();
    }
}
