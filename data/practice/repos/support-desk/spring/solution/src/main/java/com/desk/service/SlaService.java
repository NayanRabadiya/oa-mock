package com.desk.service;

import com.desk.config.DeskRules;
import com.desk.model.Ticket;
import com.desk.util.Times;
import java.time.Duration;
import java.util.Set;
import org.springframework.stereotype.Service;

@Service
public class SlaService {
    private static final Set<String> UNFINISHED = Set.of("open", "in_progress");

    public double hoursOpen(Ticket ticket, String now) {
        long seconds = Duration.between(Times.parse(ticket.createdAt()), Times.parse(now)).getSeconds();
        return seconds / (double) Times.SECONDS_PER_HOUR;
    }

    /** A ticket is overdue when it is still unfinished more than SLA_HOURS[priority] hours after it was created. */
    public boolean isOverdue(Ticket ticket, String now) {
        return UNFINISHED.contains(ticket.status()) && hoursOpen(ticket, now) > DeskRules.SLA_HOURS.get(ticket.priority());
    }
}
