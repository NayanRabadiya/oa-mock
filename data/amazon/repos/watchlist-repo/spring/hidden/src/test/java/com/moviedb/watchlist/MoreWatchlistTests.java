package com.moviedb.watchlist;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;

import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletResponse;

/** More acceptance tests (hidden in the test: they run when you submit). */
class MoreWatchlistTests extends WatchlistTestSupport {

    @Test
    void addValidationErrors() throws Exception {
        MockHttpServletResponse none = add(sam, null);
        assertEquals(400, none.getStatus());
        assertEquals("Movie ID is required", message(none));
        MockHttpServletResponse bad = add(sam, "123");
        assertEquals(400, bad.getStatus());
        assertEquals("Invalid movie ID format", message(bad));
        MockHttpServletResponse unknown = add(sam, M(999));
        assertEquals(404, unknown.getStatus());
        assertEquals("Movie not found", message(unknown));
        assertEquals(0, watchlist.count());
    }

    @Test
    void removeAndCheckValidationErrors() throws Exception {
        assertEquals("Movie ID is required", message(remove(sam, null)));
        MockHttpServletResponse bad = remove(sam, "not-an-id");
        assertEquals(400, bad.getStatus());
        assertEquals("Invalid movie ID format", message(bad));
        MockHttpServletResponse check = get(sam, "/api/watchlist/check/xyz");
        assertEquals(400, check.getStatus());
        assertEquals("Invalid movie ID format", message(check));
    }

    @Test
    void everyRouteNeedsAToken() throws Exception {
        for (MockHttpServletResponse res : List.of(get(null, "/api/watchlist/"), get(null, "/api/watchlist/check/" + M(1)),
                add(null, M(1)), remove(null, M(1)))) {
            assertEquals(401, res.getStatus());
            assertEquals("Unauthorized", message(res));
        }
    }

    @Test
    void watchlistsArePerUser() throws Exception {
        add(sam, M(1));
        add(sam, M(3));
        add(alex, M(4));
        assertEquals(List.of("The Shawshank Redemption", "The Dark Knight"), titles(sam));
        assertEquals(List.of("Spirited Away"), titles(alex));
        assertEquals(404, remove(alex, M(1)).getStatus(), "alex can't remove sam's movie");
        assertFalse(json(get(alex, "/api/watchlist/check/" + M(1))).path("isInWatchlist").asBoolean());
    }

    @Test
    void addRemoveAndAddAgain() throws Exception {
        assertEquals(201, add(sam, M(5)).getStatus());
        assertEquals(200, remove(sam, M(5)).getStatus());
        assertEquals(List.of(), titles(sam));
        assertEquals(201, add(sam, M(5)).getStatus());
        assertEquals(201, add(sam, M(2)).getStatus());
        assertEquals(List.of("Parasite", "Interstellar"), titles(sam));
    }

    @Test
    void failedRequestsCountTowardTheLimit() throws Exception {
        for (int i = 0; i < 10; i++) {
            at(i);
            assertEquals(400, add(sam, "bad" + i).getStatus());
        }
        at(10);
        assertEquals(429, add(sam, M(2)).getStatus());
        assertEquals(List.of(), titles(sam));
    }

    @Test
    void rejectedRequestsDoNotCount() throws Exception {
        for (int i = 0; i < 10; i++) {
            at(i);
            if (i % 2 == 0) {
                add(sam, M(1));
            } else {
                remove(sam, M(1));
            }
        }
        for (int t : new int[] {30, 60, 90, 119}) {
            at(t);
            assertEquals(429, add(sam, M(2)).getStatus());
        }
        at(120);
        assertEquals(201, add(sam, M(2)).getStatus(), "429 responses must not extend the window");
    }

    @Test
    void readsAreNotRateLimited() throws Exception {
        for (int i = 0; i < 10; i++) {
            at(i);
            if (i % 2 == 0) {
                add(sam, M(1));
            } else {
                remove(sam, M(1));
            }
        }
        at(11);
        for (int i = 0; i < 15; i++) {
            assertEquals(200, get(sam, "/api/watchlist/").getStatus());
            assertEquals(200, get(sam, "/api/watchlist/check/" + M(1)).getStatus());
        }
    }
}
