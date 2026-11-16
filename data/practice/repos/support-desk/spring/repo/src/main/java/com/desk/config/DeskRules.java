package com.desk.config;

import java.util.List;
import java.util.Map;

/** The support desk's rules. */
public final class DeskRules {
    /** Most urgent first. */
    public static final List<String> PRIORITIES = List.of("urgent", "high", "medium", "low");
    public static final List<String> STATUSES = List.of("open", "in_progress", "resolved", "closed");
    /** A ticket that isn't resolved within this many hours of being created is overdue. */
    public static final Map<String, Integer> SLA_HOURS = Map.of("urgent", 4, "high", 24, "medium", 72, "low", 168);

    private DeskRules() {}
}
