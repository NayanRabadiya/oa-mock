package com.returns.model;

public record EvaluateRequest(String orderId, String itemId, String reason, String requestedAt) {}
