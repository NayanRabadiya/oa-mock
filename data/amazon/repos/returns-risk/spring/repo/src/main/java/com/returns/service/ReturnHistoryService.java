package com.returns.service;

import com.returns.config.RiskRules;
import com.returns.model.History;
import com.returns.model.ReturnRecord;
import com.returns.store.ReturnStore;
import com.returns.util.Dates;
import java.util.ArrayList;
import java.util.List;
import org.springframework.stereotype.Service;

@Service
public class ReturnHistoryService {
    private final ReturnStore store;

    public ReturnHistoryService(ReturnStore store) {
        this.store = store;
    }

    /** Approved (refunded) returns of a group of accounts in the HISTORY_DAYS days before `requestedAt`. */
    public List<ReturnRecord> recentRefunds(List<String> accountIds, String requestedAt) {
        List<ReturnRecord> refunds = new ArrayList<>();
        for (String id : accountIds) {
            for (ReturnRecord ret : store.returnsForCustomer(id)) {
                long age = Dates.daysBetween(ret.date(), requestedAt);
                if (age >= 0 && age <= RiskRules.HISTORY_DAYS) {
                    refunds.add(ret);
                }
            }
        }
        return refunds;
    }

    public History summarize(List<String> accountIds, String requestedAt) {
        List<ReturnRecord> refunds = recentRefunds(accountIds, requestedAt);
        return new History(refunds.size(), refunds.stream().mapToDouble(ReturnRecord::amount).sum());
    }
}
