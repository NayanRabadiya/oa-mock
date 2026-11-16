package com.returns.model;

public record OrderItem(String id, String name, String category, double price, Integer quantity) {
    public int quantityOrOne() {
        return quantity == null ? 1 : quantity;
    }
}
