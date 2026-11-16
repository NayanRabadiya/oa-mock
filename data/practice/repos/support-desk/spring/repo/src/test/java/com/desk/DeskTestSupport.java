package com.desk;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.desk.model.Agent;
import com.desk.model.DeskData;
import com.desk.store.DeskStore;
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

/** Shared setup for the support desk tests: two agents and no tickets. */
@SpringBootTest
@AutoConfigureMockMvc
public abstract class DeskTestSupport {
    private static final ObjectMapper JSON = new ObjectMapper();

    @Autowired protected MockMvc mvc;
    @Autowired protected DeskStore store;

    @BeforeEach
    void freshData() {
        store.reset(new DeskData(List.of(new Agent("A1", "Meera", 2), new Agent("A2", "Tomas", 3)), List.of()));
    }

    protected MockHttpServletResponse post(String url, Map<String, Object> body) throws Exception {
        return mvc.perform(MockMvcRequestBuilders.post(url).contentType(MediaType.APPLICATION_JSON)
                .content(JSON.writeValueAsString(body))).andReturn().getResponse();
    }

    protected MockHttpServletResponse get(String url) throws Exception {
        return mvc.perform(MockMvcRequestBuilders.get(url)).andReturn().getResponse();
    }

    protected MockHttpServletResponse create(String priority, String createdAt) throws Exception {
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("title", "Help");
        body.put("customer", "acme");
        body.put("priority", priority);
        body.put("createdAt", createdAt);
        return post("/api/tickets", body);
    }

    protected MockHttpServletResponse create(String priority) throws Exception {
        return create(priority, "2026-11-15T09:00:00Z");
    }

    protected MockHttpServletResponse assign(String id, String agentId) throws Exception {
        return post("/api/tickets/" + id + "/assign", Map.of("agentId", agentId));
    }

    protected MockHttpServletResponse move(String id, String status, String at) throws Exception {
        return post("/api/tickets/" + id + "/status", Map.of("status", status, "at", at));
    }

    protected MockHttpServletResponse move(String id, String status) throws Exception {
        return move(id, status, "2026-11-15T12:00:00Z");
    }

    protected static JsonNode json(MockHttpServletResponse response) throws Exception {
        return JSON.readTree(response.getContentAsString());
    }

    protected static String message(MockHttpServletResponse response) throws Exception {
        return json(response).path("message").asText(null);
    }

    protected static List<String> ids(MockHttpServletResponse response) throws Exception {
        List<String> out = new ArrayList<>();
        json(response).forEach(t -> out.add(t.path("id").asText()));
        return out;
    }
}
