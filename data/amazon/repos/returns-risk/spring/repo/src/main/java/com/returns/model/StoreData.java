package com.returns.model;

import java.util.List;

/** A data set for the store: what src/main/resources/seed.json holds. */
public record StoreData(List<Customer> customers, List<Order> orders, List<ReturnRecord> returns) {}
