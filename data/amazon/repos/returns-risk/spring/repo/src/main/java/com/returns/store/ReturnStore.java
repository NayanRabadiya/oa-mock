package com.returns.store;

import com.returns.model.Customer;
import com.returns.model.Order;
import com.returns.model.ReturnRecord;
import com.returns.model.StoreData;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Component;

/**
 * An in-memory store standing in for the customer, order and returns databases. reset() loads a data set
 * (seed.json when the app starts; the tests load their own).
 */
@Component
public class ReturnStore {
    private Map<String, Customer> customers = new LinkedHashMap<>();
    private Map<String, Order> orders = new LinkedHashMap<>();
    private List<ReturnRecord> returns = new ArrayList<>();
    private int nextReturnId = 1;

    public synchronized void reset(StoreData data) {
        customers = new LinkedHashMap<>();
        orders = new LinkedHashMap<>();
        returns = new ArrayList<>();
        if (data != null) {
            if (data.customers() != null) data.customers().forEach(c -> customers.put(c.id(), c));
            if (data.orders() != null) data.orders().forEach(o -> orders.put(o.id(), o));
            if (data.returns() != null) returns.addAll(data.returns());
        }
        nextReturnId = returns.size() + 1;
    }

    public synchronized Customer getCustomer(String id) {
        return customers.get(id);
    }

    public synchronized Order getOrder(String id) {
        return orders.get(id);
    }

    public synchronized List<ReturnRecord> returnsForCustomer(String customerId) {
        return returns.stream().filter(r -> customerId.equals(r.customerId())).toList();
    }

    public synchronized List<ReturnRecord> returnsForItem(String orderId, String itemId) {
        return returns.stream().filter(r -> orderId.equals(r.orderId()) && itemId.equals(r.itemId())).toList();
    }

    public synchronized ReturnRecord addReturn(ReturnRecord record) {
        ReturnRecord saved = record.withId(String.format("RET-%04d", nextReturnId++));
        returns.add(saved);
        return saved;
    }
}
