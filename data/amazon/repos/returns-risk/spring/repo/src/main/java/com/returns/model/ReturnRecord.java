package com.returns.model;

import com.fasterxml.jackson.annotation.JsonInclude;

/** One entry of the return history. status is APPROVED, PENDING_REVIEW or REJECTED. */
@JsonInclude(JsonInclude.Include.NON_NULL)
public record ReturnRecord(String id, String customerId, String orderId, String itemId, String status, double amount,
                           String date, String reason) {
    public ReturnRecord withId(String newId) {
        return new ReturnRecord(newId, customerId, orderId, itemId, status, amount, date, reason);
    }
}
