package com.returns.model;

import java.util.List;

public record Customer(String id, String name, String createdAt, List<String> linkedAccountIds) {
    public Customer {
        linkedAccountIds = linkedAccountIds == null ? List.of() : List.copyOf(linkedAccountIds);
    }
}
