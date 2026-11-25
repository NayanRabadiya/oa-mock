package com.returns.service;

import com.returns.config.RiskRules;
import com.returns.model.Evaluation;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Service;

@Service
public class DecisionService {
    /** What the service decides, and what it stores in the return history for that decision. */
    public static final Map<String, String> STATUS_FOR =
            Map.of("AUTO_APPROVE", "APPROVED", "MANUAL_REVIEW", "PENDING_REVIEW", "REJECT", "REJECTED");

    public Evaluation decide(int score, List<String> reasons) {
        String decision = "AUTO_APPROVE";
        List<String> codes = new ArrayList<>(reasons);

        if (score > RiskRules.REJECT_FROM) {
            decision = "REJECT";
            codes.add("HIGH_RISK");
        } else if (score >= RiskRules.MANUAL_REVIEW_FROM) {
            decision = "MANUAL_REVIEW";
        }

        return new Evaluation(decision, score, codes, ReasonCodes.messagesFor(codes));
    }

    /** A request that breaks an eligibility rule is rejected with just that reason. */
    public Evaluation ineligible(String code) {
        return new Evaluation("REJECT", 0, List.of(code), ReasonCodes.messagesFor(List.of(code)));
    }
}
