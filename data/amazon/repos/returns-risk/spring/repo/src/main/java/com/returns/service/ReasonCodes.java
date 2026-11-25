package com.returns.service;

import java.util.List;
import java.util.Map;

/** Every reason code the service can return, with the text shown to support agents. */
public final class ReasonCodes {
    public static final Map<String, String> REASON_MESSAGES = Map.ofEntries(
            Map.entry("NOT_DELIVERED", "The order hasn't been delivered yet"),
            Map.entry("ALREADY_RETURNED", "This item already has an approved or pending return"),
            Map.entry("NON_RETURNABLE_CATEGORY", "Items in this category can't be returned"),
            Map.entry("RETURN_WINDOW_EXPIRED", "The return window for this category has passed"),
            Map.entry("REASON_NOT_AS_DESCRIBED", "The customer says the item is not as described"),
            Map.entry("REASON_DISCRETIONARY", "The customer changed their mind or no longer needs the item"),
            Map.entry("ORDER_VALUE_HIGH", "The return is worth 500 or more"),
            Map.entry("ORDER_VALUE_ELEVATED", "The return is worth 200 or more"),
            Map.entry("ORDER_VALUE_MODERATE", "The return is worth 50 or more"),
            Map.entry("RETURN_FREQUENCY", "Linked accounts had approved returns in the last 90 days"),
            Map.entry("REFUND_TOTAL_HIGH", "Linked accounts were refunded more than 1000 in the last 90 days"),
            Map.entry("NEW_ACCOUNT", "The account is less than 30 days old"),
            Map.entry("HIGH_RISK", "The risk score is 70 or more"));

    private ReasonCodes() {}

    public static List<String> messagesFor(List<String> codes) {
        return codes.stream().map(code -> REASON_MESSAGES.getOrDefault(code, code)).toList();
    }
}
