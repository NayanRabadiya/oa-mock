package com.moviedb.watchlist;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.moviedb.model.Watchlist;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletResponse;

/** The acceptance tests for the watchlist feature. Run them with:  mvn test */
class WatchlistTests extends WatchlistTestSupport {

    @Test
    void getWatchlistReturnsMoviesInOrderAdded() throws Exception {
        watchlist.save(new Watchlist(sam.getId(), movies.findById(M(3)).orElseThrow()));
        watchlist.save(new Watchlist(sam.getId(), movies.findById(M(1)).orElseThrow()));
        watchlist.save(new Watchlist(alex.getId(), movies.findById(M(2)).orElseThrow()));
        MockHttpServletResponse res = get(sam, "/api/watchlist/");
        assertEquals(200, res.getStatus(), res.getContentAsString());
        JsonNode body = json(res);
        assertEquals(List.of("The Dark Knight", "The Shawshank Redemption"), titles(sam));
        assertEquals(M(3), body.get(0).path("id").asText(), "each item is a movie document");
        assertTrue(body.get(0).has("year"), "each item is a movie document");
    }

    @Test
    void addMovieCreatesEntryAndRejectsDuplicates() throws Exception {
        MockHttpServletResponse first = add(sam, M(2));
        assertEquals(201, first.getStatus(), first.getContentAsString());
        assertEquals("Movie added to watchlist successfully", message(first));
        assertTrue(watchlist.existsByUserIdAndMovieId(sam.getId(), M(2)), "the entry must be saved");
        MockHttpServletResponse again = add(sam, M(2));
        assertEquals(400, again.getStatus(), again.getContentAsString());
        assertEquals("Movie already in watchlist", message(again));
        assertEquals(1, watchlist.findByUserIdOrderByCreatedAtAscIdAsc(sam.getId()).size());
    }

    @Test
    void removeMovieDeletesEntryAnd404WhenMissing() throws Exception {
        watchlist.save(new Watchlist(sam.getId(), movies.findById(M(4)).orElseThrow()));
        MockHttpServletResponse removed = remove(sam, M(4));
        assertEquals(200, removed.getStatus(), removed.getContentAsString());
        assertEquals("Movie removed from watchlist successfully", message(removed));
        assertFalse(watchlist.existsByUserIdAndMovieId(sam.getId(), M(4)), "the entry must be deleted");
        MockHttpServletResponse missing = remove(sam, M(4));
        assertEquals(404, missing.getStatus(), missing.getContentAsString());
        assertEquals("Movie not found in watchlist", message(missing));
    }

    @Test
    void checkStatusReturnsBoolean() throws Exception {
        MockHttpServletResponse before = get(sam, "/api/watchlist/check/" + M(5));
        assertEquals(200, before.getStatus(), before.getContentAsString());
        assertTrue(json(before).path("isInWatchlist").isBoolean(), "isInWatchlist must be true or false: " + before.getContentAsString());
        assertFalse(json(before).path("isInWatchlist").asBoolean());
        watchlist.save(new Watchlist(sam.getId(), movies.findById(M(5)).orElseThrow()));
        MockHttpServletResponse after = get(sam, "/api/watchlist/check/" + M(5));
        assertTrue(json(after).path("isInWatchlist").isBoolean() && json(after).path("isInWatchlist").asBoolean(), after.getContentAsString());
    }

    @Test
    void rateLimitBlocksEleventhOperationCombined() throws Exception {
        for (int i = 0; i < 5; i++) {
            at(i * 2);
            assertEquals(201, add(sam, M(i + 1)).getStatus());
            at(i * 2 + 1);
            assertEquals(200, remove(sam, M(i + 1)).getStatus());
        }
        at(11);
        MockHttpServletResponse blocked = add(sam, M(6));
        assertEquals(429, blocked.getStatus(), "adds and removes share one limit of 10 per 2 minutes");
        assertEquals(LIMIT, message(blocked));
        assertEquals(201, add(alex, M(6)).getStatus(), "the limit is per user");
    }

    @Test
    void rateLimitWindowSlidesAfterTwoMinutes() throws Exception {
        for (int i = 0; i < 10; i++) {
            at(i);
            if (i % 2 == 0) {
                add(sam, M(1));
            } else {
                remove(sam, M(1));
            }
        }
        at(60);
        assertEquals(429, add(sam, M(2)).getStatus());
        at(120);
        assertEquals(201, add(sam, M(2)).getStatus(), "the request made at 0 s stops counting at 120 s");
        assertEquals(429, add(sam, M(3)).getStatus(), "at 120 s the window holds 10 again");
        at(121);
        assertEquals(201, add(sam, M(3)).getStatus());
    }
}
