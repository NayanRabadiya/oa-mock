package com.wallet;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.wallet.model.Wallet;
import com.wallet.model.WalletData;
import com.wallet.store.WalletStore;
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

/** Shared setup for the wallet tests: three wallets, no transactions yet. */
@SpringBootTest
@AutoConfigureMockMvc
public abstract class WalletTestSupport {
    private static final ObjectMapper JSON = new ObjectMapper();

    @Autowired protected MockMvc mvc;
    @Autowired protected WalletStore store;

    @BeforeEach
    void freshData() {
        store.reset(new WalletData(List.of(new Wallet("W1", "Asha", 1000, "active"), new Wallet("W2", "Bilal", 200, "active"),
                new Wallet("W3", "Chen", 500, "frozen")), List.of()));
    }

    protected MockHttpServletResponse post(String url, Map<String, Object> body) throws Exception {
        return mvc.perform(MockMvcRequestBuilders.post(url).contentType(MediaType.APPLICATION_JSON)
                .content(JSON.writeValueAsString(body))).andReturn().getResponse();
    }

    protected MockHttpServletResponse get(String url) throws Exception {
        return mvc.perform(MockMvcRequestBuilders.get(url)).andReturn().getResponse();
    }

    protected MockHttpServletResponse deposit(String id, Object amount, String at) throws Exception {
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("amount", amount);
        body.put("at", at);
        return post("/api/wallets/" + id + "/deposit", body);
    }

    protected MockHttpServletResponse deposit(String id, Object amount) throws Exception {
        return deposit(id, amount, "2026-11-15T09:00:00Z");
    }

    protected MockHttpServletResponse withdraw(String id, Object amount) throws Exception {
        return post("/api/wallets/" + id + "/withdraw", Map.of("amount", amount, "at", "2026-11-15T09:00:00Z"));
    }

    protected MockHttpServletResponse send(String from, String to, Object amount, String at) throws Exception {
        return post("/api/transfers", Map.of("from", from, "to", to, "amount", amount, "at", at));
    }

    protected MockHttpServletResponse send(String from, String to, Object amount) throws Exception {
        return send(from, to, amount, "2026-11-15T10:00:00Z");
    }

    protected MockHttpServletResponse wallet(String id) throws Exception {
        return get("/api/wallets/" + id);
    }

    protected MockHttpServletResponse history(String id, String query) throws Exception {
        return get("/api/wallets/" + id + "/transactions" + query);
    }

    protected MockHttpServletResponse history(String id) throws Exception {
        return history(id, "");
    }

    protected static JsonNode json(MockHttpServletResponse response) throws Exception {
        return JSON.readTree(response.getContentAsString());
    }

    protected static String message(MockHttpServletResponse response) throws Exception {
        return json(response).path("message").asText(null);
    }

    protected static long balance(MockHttpServletResponse response) throws Exception {
        return json(response).path("balance").asLong();
    }

    /** One field of every element of a JSON array, as text. */
    protected static List<String> each(MockHttpServletResponse response, String field) throws Exception {
        List<String> out = new ArrayList<>();
        json(response).forEach(t -> out.add(t.path(field).asText()));
        return out;
    }
}
