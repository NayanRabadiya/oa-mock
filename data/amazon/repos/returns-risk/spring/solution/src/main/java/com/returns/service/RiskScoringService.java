package com.returns.service;

import com.returns.config.RiskRules;
import com.returns.model.Customer;
import com.returns.model.History;
import com.returns.model.OrderItem;
import com.returns.util.Dates;
import java.util.ArrayList;
import java.util.List;
import org.springframework.stereotype.Service;

@Service
public class RiskScoringService {
    public record Score(int score, List<String> reasons) {}

    /**
     * Adds up the risk points for one return. The reasons are the codes of every rule that added points, in this
     * order: return reason, value, history, refund total, account age.
     */
    public Score scoreReturn(OrderItem item, String reason, Customer customer, History history, String requestedAt) {
        int score = 0;
        List<String> reasons = new ArrayList<>();

        int reasonPoints = RiskRules.REASON_POINTS.getOrDefault(reason, 0);
        if (reasonPoints > 0) {
            score += reasonPoints;
            reasons.add("NOT_AS_DESCRIBED".equals(reason) ? "REASON_NOT_AS_DESCRIBED" : "REASON_DISCRETIONARY");
        }

        double value = item.price() * item.quantityOrOne();
        for (RiskRules.ValueTier tier : RiskRules.VALUE_TIERS) {
            if (value >= tier.min()) {
                score += tier.points();
                reasons.add(tier.code());
                break;
            }
        }

        if (history.count() > 0) {
            score += Math.min(history.count() * RiskRules.POINTS_PER_RECENT_RETURN, RiskRules.MAX_HISTORY_POINTS);
            reasons.add("RETURN_FREQUENCY");
        }

        if (history.total() > RiskRules.REFUND_TOTAL_LIMIT) {
            score += RiskRules.REFUND_TOTAL_POINTS;
            reasons.add("REFUND_TOTAL_HIGH");
        }

        if (customer.createdAt() != null
                && Dates.daysBetween(customer.createdAt(), requestedAt) < RiskRules.NEW_ACCOUNT_DAYS) {
            score += RiskRules.NEW_ACCOUNT_POINTS;
            reasons.add("NEW_ACCOUNT");
        }

        return new Score(Math.min(score, RiskRules.MAX_SCORE), reasons);
    }
}
