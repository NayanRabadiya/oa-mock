package com.library;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.library.model.Book;
import com.library.model.LibraryData;
import com.library.model.Member;
import com.library.store.LibraryStore;
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

/** Shared setup for the library tests: a fresh store with three books and two members. */
@SpringBootTest
@AutoConfigureMockMvc
public abstract class LibraryTestSupport {
    private static final ObjectMapper JSON = new ObjectMapper();

    @Autowired protected MockMvc mvc;
    @Autowired protected LibraryStore store;

    @BeforeEach
    void freshData() {
        store.reset(new LibraryData(
                List.of(new Book("B1", "The Pragmatic Programmer", 2), new Book("B2", "Clean Code", 1),
                        new Book("B3", "Refactoring", 5)),
                List.of(new Member("M1", "Asha"), new Member("M2", "Bilal")),
                List.of()));
    }

    protected MockHttpServletResponse post(String url, Map<String, Object> body) throws Exception {
        return mvc.perform(MockMvcRequestBuilders.post(url).contentType(MediaType.APPLICATION_JSON)
                .content(JSON.writeValueAsString(body))).andReturn().getResponse();
    }

    protected MockHttpServletResponse borrow(String memberId, String bookId, String borrowedAt) throws Exception {
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("memberId", memberId);
        body.put("bookId", bookId);
        body.put("borrowedAt", borrowedAt);
        return post("/api/loans", body);
    }

    protected MockHttpServletResponse borrow(String memberId, String bookId) throws Exception {
        return borrow(memberId, bookId, "2026-11-01");
    }

    protected MockHttpServletResponse giveBack(String loanId, String returnedAt) throws Exception {
        return post("/api/loans/" + loanId + "/return", Map.of("returnedAt", returnedAt));
    }

    protected int available(String bookId) throws Exception {
        JsonNode books = json(mvc.perform(MockMvcRequestBuilders.get("/api/books")).andReturn().getResponse());
        for (JsonNode book : books) {
            if (book.path("id").asText().equals(bookId)) {
                return book.path("available").asInt();
            }
        }
        throw new AssertionError("no book " + bookId);
    }

    protected static JsonNode json(MockHttpServletResponse response) throws Exception {
        return JSON.readTree(response.getContentAsString());
    }

    protected static String message(MockHttpServletResponse response) throws Exception {
        return json(response).path("message").asText(null);
    }
}
