package com.returns.config;

import java.util.List;
import java.util.Map;

/** Points that make up a return's risk score (0-100), and the decision thresholds. */
public final class RiskRules {
    public record ValueTier(double min, int points, String code) {}

    public static final Map<String, Integer> REASON_POINTS = Map.of(
            "DAMAGED", 0,
            "WRONG_ITEM", 0,
            "NOT_AS_DESCRIBED", 10,
            "CHANGED_MIND", 20,
            "NO_LONGER_NEEDED", 20);

    /** The value being returned is price x quantity. */
    public static final List<ValueTier> VALUE_TIERS = List.of(
            new ValueTier(500, 25, "ORDER_VALUE_HIGH"),
            new ValueTier(200, 15, "ORDER_VALUE_ELEVATED"),
            new ValueTier(50, 5, "ORDER_VALUE_MODERATE"));

    public static final int HISTORY_DAYS = 90;              // approved returns in the 90 days before the request
    public static final int POINTS_PER_RECENT_RETURN = 10;
    public static final int MAX_HISTORY_POINTS = 40;
    public static final double REFUND_TOTAL_LIMIT = 1000;   // more than this refunded in the 90 days
    public static final int REFUND_TOTAL_POINTS = 15;
    public static final int NEW_ACCOUNT_DAYS = 30;          // account created less than 30 days before the request
    public static final int NEW_ACCOUNT_POINTS = 10;
    public static final int MAX_SCORE = 100;
    public static final int MANUAL_REVIEW_FROM = 30;        // 30-69: manual review
    public static final int REJECT_FROM = 70;               // 70 and above: reject

    private RiskRules() {}
}
