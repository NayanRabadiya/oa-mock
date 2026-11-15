package com.returns.service;

import com.returns.config.ReturnPolicy;
import com.returns.model.Order;
import com.returns.model.OrderItem;
import com.returns.store.ReturnStore;
import com.returns.util.Dates;
import org.springframework.stereotype.Service;

@Service
public class EligibilityService {
    private final ReturnStore store;

    public EligibilityService(ReturnStore store) {
        this.store = store;
    }

    /**
     * The first rule a return request breaks, as a reason code, or null when it may be returned. Rules are checked
     * in this order: delivered, not already returned, returnable category, inside the window.
     */
    public String checkEligibility(Order order, OrderItem item, String requestedAt) {
        if (!"DELIVERED".equals(order.status()) || order.deliveredAt() == null) {
            return "NOT_DELIVERED";
        }

        boolean open = store.returnsForItem(order.id(), item.id()).stream()
                .anyMatch(r -> "APPROVED".equals(r.status()) || "PENDING_REVIEW".equals(r.status()));
        if (open) {
            return "ALREADY_RETURNED";
        }

        ReturnPolicy.Policy policy = ReturnPolicy.getPolicy(item.category());
        if (!policy.returnable()) {
            return "NON_RETURNABLE_CATEGORY";
        }

        long daysSinceDelivery = Dates.daysBetween(order.deliveredAt(), requestedAt);
        if (daysSinceDelivery >= policy.windowDays()) {
            return "RETURN_WINDOW_EXPIRED";
        }

        return null;
    }
}
