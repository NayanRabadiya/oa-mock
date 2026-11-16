package com.returns.model;

import java.util.List;

public record Order(String id, String customerId, String status, String deliveredAt, List<OrderItem> items) {
    public Order {
        items = items == null ? List.of() : List.copyOf(items);
    }
}
