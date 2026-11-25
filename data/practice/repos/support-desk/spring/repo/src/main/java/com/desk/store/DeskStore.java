package com.desk.store;

import com.desk.model.Agent;
import com.desk.model.DeskData;
import com.desk.model.Ticket;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Component;

/**
 * An in-memory store standing in for the help desk database. reset() loads a data set (seed.json when the app
 * starts; the tests load their own).
 */
@Component
public class DeskStore {
    private Map<String, Agent> agents = new LinkedHashMap<>();
    private List<Ticket> tickets = new ArrayList<>();
    private int nextId = 1;

    public synchronized void reset(DeskData data) {
        agents = new LinkedHashMap<>();
        tickets = new ArrayList<>();
        if (data != null) {
            if (data.agents() != null) data.agents().forEach(a -> agents.put(a.id(), a));
            if (data.tickets() != null) tickets.addAll(data.tickets());
        }
        nextId = tickets.size() + 1;
    }

    public synchronized Agent getAgent(String id) {
        return id == null ? null : agents.get(id);
    }

    public synchronized List<Ticket> allTickets() {
        return List.copyOf(tickets);
    }

    public synchronized Ticket getTicket(String id) {
        return tickets.stream().filter(t -> t.id().equals(id)).findFirst().orElse(null);
    }

    public synchronized Ticket addTicket(Ticket ticket) {
        Ticket saved = ticket.withId("T" + nextId++);
        tickets.add(saved);
        return saved;
    }

    public synchronized Ticket save(Ticket ticket) {
        for (int i = 0; i < tickets.size(); i++) {
            if (tickets.get(i).id().equals(ticket.id())) {
                tickets.set(i, ticket);
            }
        }
        return ticket;
    }
}
