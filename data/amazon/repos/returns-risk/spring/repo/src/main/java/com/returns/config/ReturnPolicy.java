package com.returns.config;

import java.util.Map;

/**
 * Which product categories can be returned, and within how many days of delivery. Orders store the category the
 * way the catalogue shows it ("Electronics", "Home & Kitchen" ...); policy keys are lowercase.
 */
public final class ReturnPolicy {
    public record Policy(boolean returnable, int windowDays) {}

    public static final Map<String, Policy> RETURN_POLICY = Map.of(
            "electronics", new Policy(true, 30),
            "apparel", new Policy(true, 45),
            "home & kitchen", new Policy(true, 30),
            "books", new Policy(true, 14),
            "jewelry", new Policy(true, 15),
            "grocery", new Policy(false, 0),
            "digital content", new Policy(false, 0),
            "gift cards", new Policy(false, 0));

    /** Unknown categories can't be returned. */
    public static final Policy NOT_RETURNABLE = new Policy(false, 0);

    private ReturnPolicy() {}

    public static Policy getPolicy(String category) {
        String key = category == null ? "" : category.trim();
        return RETURN_POLICY.getOrDefault(key, NOT_RETURNABLE);
    }
}
