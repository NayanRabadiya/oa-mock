package com.returns.controller;

import com.returns.config.RiskRules;
import com.returns.model.Customer;
import com.returns.model.EvaluateRequest;
import com.returns.model.Evaluation;
import com.returns.model.History;
import com.returns.model.Order;
import com.returns.model.OrderItem;
import com.returns.model.ReturnRecord;
import com.returns.service.DecisionService;
import com.returns.service.EligibilityService;
import com.returns.service.LinkedAccountService;
import com.returns.service.ReturnHistoryService;
import com.returns.service.RiskScoringService;
import com.returns.store.ReturnStore;
import com.returns.util.Dates;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/returns")
public class ReturnController {
    private static final Logger log = LoggerFactory.getLogger(ReturnController.class);

    private final ReturnStore store;
    private final EligibilityService eligibility;
    private final LinkedAccountService linkedAccounts;
    private final ReturnHistoryService history;
    private final RiskScoringService scoring;
    private final DecisionService decisions;

    public ReturnController(ReturnStore store, EligibilityService eligibility, LinkedAccountService linkedAccounts,
                            ReturnHistoryService history, RiskScoringService scoring, DecisionService decisions) {
        this.store = store;
        this.eligibility = eligibility;
        this.linkedAccounts = linkedAccounts;
        this.history = history;
        this.scoring = scoring;
        this.decisions = decisions;
    }

    private static ResponseEntity<Map<String, String>> error(int status, String message) {
        return ResponseEntity.status(status).body(Map.of("message", message));
    }

    private static boolean blank(String value) {
        return value == null || value.isEmpty();
    }

    /** POST /api/returns/evaluate  {orderId, itemId, reason, requestedAt?} */
    @PostMapping("/evaluate")
    public ResponseEntity<?> evaluateReturn(@RequestBody(required = false) EvaluateRequest body) {
        try {
            EvaluateRequest req = body == null ? new EvaluateRequest(null, null, null, null) : body;
            String requestedAt = req.requestedAt() == null ? Dates.today() : req.requestedAt();

            if (blank(req.orderId()) || blank(req.itemId()) || blank(req.reason())) {
                return error(400, "orderId, itemId and reason are required");
            }
            if (!RiskRules.REASON_POINTS.containsKey(req.reason())) {
                return error(400, "Invalid return reason");
            }
            if (!Dates.isIsoDate(requestedAt)) {
                return error(400, "requestedAt must be a date like 2026-11-15");
            }

            Order order = store.getOrder(req.orderId());
            if (order == null) {
                return error(404, "Order not found");
            }
            OrderItem item = order.items().stream().filter(i -> req.itemId().equals(i.id())).findFirst().orElse(null);
            if (item == null) {
                return error(404, "Item not found in order");
            }
            Customer found = store.getCustomer(order.customerId());
            Customer customer = found != null ? found : new Customer(order.customerId(), null, null, List.of());

            Evaluation result;
            String blocked = eligibility.checkEligibility(order, item, requestedAt);
            if (blocked != null) {
                result = decisions.ineligible(blocked);
            } else {
                List<String> group = linkedAccounts.getAccountGroup(customer.id());
                History recent = history.summarize(group, requestedAt);
                RiskScoringService.Score score = scoring.scoreReturn(item, req.reason(), customer, recent, requestedAt);
                result = decisions.decide(score.score(), score.reasons());
            }

            ReturnRecord record = store.addReturn(new ReturnRecord(null, customer.id(), req.orderId(), req.itemId(),
                    DecisionService.STATUS_FOR.get(result.decision()), item.price() * item.quantityOrOne(),
                    requestedAt, req.reason()));

            Map<String, Object> response = new LinkedHashMap<>();
            response.put("returnId", record.id());
            response.put("decision", result.decision());
            response.put("riskScore", result.riskScore());
            response.put("reasons", result.reasons());
            response.put("messages", result.messages());
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            log.error("Evaluate return error", e);
            return error(500, "Server error");
        }
    }

    /** GET /api/returns/customer/{customerId}  every return request of one customer, oldest first */
    @GetMapping("/customer/{customerId}")
    public ResponseEntity<?> getCustomerReturns(@PathVariable String customerId) {
        if (store.getCustomer(customerId) == null) {
            return error(404, "Customer not found");
        }
        return ResponseEntity.ok(store.returnsForCustomer(customerId));
    }
}
