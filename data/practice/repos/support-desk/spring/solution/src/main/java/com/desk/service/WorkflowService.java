package com.desk.service;

import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Service;

@Service
public class WorkflowService {
    /**
     * Where a ticket can go from each status. A resolved ticket can be reopened (back to in_progress) or closed;
     * a closed ticket is final.
     */
    private static final Map<String, List<String>> NEXT = Map.of(
            "open", List.of("in_progress"),
            "in_progress", List.of("resolved"),
            "resolved", List.of("in_progress", "closed"),
            "closed", List.of());

    public boolean canMove(String from, String to) {
        return NEXT.getOrDefault(from, List.of()).contains(to);
    }
}
