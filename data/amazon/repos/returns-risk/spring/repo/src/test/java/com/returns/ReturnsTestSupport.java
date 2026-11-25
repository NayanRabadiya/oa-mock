package com.returns;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.returns.model.Customer;
import com.returns.model.Order;
import com.returns.model.OrderItem;
import com.returns.model.ReturnRecord;
import com.returns.model.StoreData;
import com.returns.store.ReturnStore;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * Shared setup for the return/risk tests: a fresh store with linked accounts, plus helpers to add orders and past
 * returns and to call the API.
 */
@SpringBootTest
@AutoConfigureMockMvc
public abstract class ReturnsTestSupport {
    protected static final String TODAY = "2026-11-15";
    private static final ObjectMapper JSON = new ObjectMapper();

    @Autowired protected MockMvc mvc;
    @Autowired protected ReturnStore store;

    private List<Customer> customers;
    private List<Order> orders;
    private List<ReturnRecord> returns;

    @BeforeEach
    void freshData() {
        // C1 - C2 - C3 are linked in a chain; C5 has no links; C9 opened their account on 2026-11-01.
        customers = List.of(
                new Customer("C1", "Asha", "2024-01-01", List.of("C2")),
                new Customer("C2", "Bilal", "2024-01-01", List.of("C1", "C3")),
                new Customer("C3", "Chen", "2024-01-01", List.of("C2")),
                new Customer("C5", "Dev", "2024-01-01", List.of()),
                new Customer("C9", "Esha", "2026-11-01", List.of()));
        orders = new ArrayList<>();
        returns = new ArrayList<>();
        reload();
    }

    private void reload() {
        store.reset(new StoreData(customers, orders, returns));
    }

    /** A delivered order with one item (id I-1). */
    protected void order(String orderId, String customerId, String deliveredAt, String category, double price, int quantity) {
        order(orderId, customerId, "DELIVERED", deliveredAt, category, price, quantity);
    }

    protected void order(String orderId, String customerId, String status, String deliveredAt, String category,
                         double price, int quantity) {
        orders.add(new Order(orderId, customerId, status, deliveredAt,
                List.of(new OrderItem("I-1", "Item", category, price, quantity))));
        reload();
    }

    /** A delivered Electronics order worth `price`, delivered on 2026-11-01. */
    protected void order(String orderId, String customerId, double price) {
        order(orderId, customerId, "2026-11-01", "Electronics", price, 1);
    }

    /** A past return in the history. */
    protected void pastReturn(String customerId, String status, double amount, String date, String orderId) {
        int n = returns.size() + 1;
        returns.add(new ReturnRecord("R" + n, customerId, orderId == null ? "OLD-" + n : orderId, "I-1", status,
                amount, date, null));
        reload();
    }

    protected void pastReturn(String customerId, String status, double amount, String date) {
        pastReturn(customerId, status, amount, date, null);
    }

    protected void pastReturn(String customerId) {
        pastReturn(customerId, "APPROVED", 100, "2026-10-20", null);
    }

    protected MockHttpServletResponse post(Map<String, Object> body) throws Exception {
        return mvc.perform(MockMvcRequestBuilders.post("/api/returns/evaluate")
                .contentType(MediaType.APPLICATION_JSON).content(JSON.writeValueAsString(body))).andReturn().getResponse();
    }

    protected MockHttpServletResponse get(String url) throws Exception {
        return mvc.perform(MockMvcRequestBuilders.get(url)).andReturn().getResponse();
    }

    /** POST /api/returns/evaluate for item I-1 of the order, requested today; `extra` is key, value, key, value ... */
    protected MockHttpServletResponse evaluateResponse(String orderId, String reason, Object... extra) throws Exception {
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("orderId", orderId);
        body.put("itemId", "I-1");
        body.put("reason", reason);
        body.put("requestedAt", TODAY);
        for (int i = 0; i + 1 < extra.length; i += 2) {
            body.put((String) extra[i], extra[i + 1]);
        }
        return post(body);
    }

    protected JsonNode evaluate(String orderId, String reason, Object... extra) throws Exception {
        MockHttpServletResponse res = evaluateResponse(orderId, reason, extra);
        assertEquals(200, res.getStatus(), res.getContentAsString());
        return json(res);
    }

    protected JsonNode evaluate(String orderId) throws Exception {
        return evaluate(orderId, "DAMAGED");
    }

    protected static JsonNode json(MockHttpServletResponse response) throws Exception {
        return JSON.readTree(response.getContentAsString());
    }

    protected static List<String> strings(JsonNode array) {
        List<String> out = new ArrayList<>();
        array.forEach(node -> out.add(node.asText()));
        return out;
    }

    /** Checks the decision, the score and the reasons of an evaluation (null skips that part). */
    protected static void assertEvaluation(JsonNode body, String decision, Integer riskScore, List<String> reasons) {
        if (decision != null) assertEquals(decision, body.path("decision").asText(), body.toString());
        if (riskScore != null) assertEquals(riskScore.intValue(), body.path("riskScore").asInt(), body.toString());
        if (reasons != null) assertEquals(reasons, strings(body.path("reasons")), body.toString());
    }
}
