package com.returns.model;

import java.util.List;

/** The outcome of evaluating one return request. */
public record Evaluation(String decision, int riskScore, List<String> reasons, List<String> messages) {}
