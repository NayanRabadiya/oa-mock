package com.returns.service;

import com.returns.model.Customer;
import com.returns.store.ReturnStore;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import org.springframework.stereotype.Service;

@Service
public class LinkedAccountService {
    private final ReturnStore store;

    public LinkedAccountService(ReturnStore store) {
        this.store = store;
    }

    /**
     * Accounts are linked when they share a household, address or payment method. Links can chain (A is linked to
     * B, B to C), and every account in the chain belongs to the same group. Returns the ids of the whole group, the
     * customer first.
     */
    public List<String> getAccountGroup(String customerId) {
        Customer customer = store.getCustomer(customerId);
        List<String> group = new ArrayList<>(List.of(customerId));
        if (customer != null) {
            customer.linkedAccountIds().stream().filter(id -> !id.equals(customerId)).forEach(group::add);
        }

        return group;
    }
}
