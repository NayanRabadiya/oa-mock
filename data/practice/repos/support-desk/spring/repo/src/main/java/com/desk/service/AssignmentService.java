package com.desk.service;

import com.desk.model.Agent;
import com.desk.model.Ticket;
import com.desk.store.DeskStore;
import java.util.Set;
import org.springframework.stereotype.Service;

@Service
public class AssignmentService {
    private static final Set<String> ACTIVE = Set.of("open");

    private final DeskStore store;

    public AssignmentService(DeskStore store) {
        this.store = store;
    }

    /** How many unfinished tickets an agent has, not counting `exceptId`. */
    public long workload(String agentId, String exceptId) {
        return store.allTickets().stream()
                .filter(t -> agentId.equals(t.assigneeId()) && !t.id().equals(exceptId) && ACTIVE.contains(t.status()))
                .count();
    }

    /** An agent can take a ticket while they have fewer than maxOpen unfinished tickets. */
    public boolean canTake(Agent agent, Ticket ticket) {
        return workload(agent.id(), ticket.id()) < agent.maxOpen();
    }
}
