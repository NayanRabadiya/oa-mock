package com.desk.model;

/** A ticket; assigneeId and resolvedAt are null until it is assigned or resolved. */
public record Ticket(String id, String title, String customer, String priority, String status, String assigneeId,
                     String createdAt, String resolvedAt) {
    public Ticket withId(String newId) {
        return new Ticket(newId, title, customer, priority, status, assigneeId, createdAt, resolvedAt);
    }

    public Ticket withAssignee(String agentId, String newStatus) {
        return new Ticket(id, title, customer, priority, newStatus, agentId, createdAt, resolvedAt);
    }

    public Ticket withStatus(String newStatus, String newResolvedAt) {
        return new Ticket(id, title, customer, priority, newStatus, assigneeId, createdAt, newResolvedAt);
    }

    public int number() {
        return Integer.parseInt(id.substring(1));
    }
}
