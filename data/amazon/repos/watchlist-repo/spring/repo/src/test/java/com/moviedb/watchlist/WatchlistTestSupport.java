package com.moviedb.watchlist;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.moviedb.model.ApiToken;
import com.moviedb.model.Movie;
import com.moviedb.model.User;
import com.moviedb.ratelimit.WatchlistRateLimiter;
import com.moviedb.repository.ApiTokenRepository;
import com.moviedb.repository.MovieRepository;
import com.moviedb.repository.RatingRepository;
import com.moviedb.repository.UserRepository;
import com.moviedb.repository.WatchlistRepository;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.request.MockHttpServletRequestBuilder;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;

/** Shared setup for the watchlist tests: a fresh database with the sample movies and two users. */
@SpringBootTest
@AutoConfigureMockMvc
public abstract class WatchlistTestSupport {
    protected static final String[] TITLES = {"The Shawshank Redemption", "Interstellar", "The Dark Knight",
            "Spirited Away", "Parasite", "Inception"};
    protected static final String LIMIT =
            "Too many watchlist operations. You can add or remove movies up to 10 times within 2 minutes.";
    private static final long START = 1_700_000_000_000L;
    private static final ObjectMapper JSON = new ObjectMapper();

    @Autowired protected MockMvc mvc;
    @Autowired protected MovieRepository movies;
    @Autowired protected UserRepository users;
    @Autowired protected WatchlistRepository watchlist;
    @Autowired protected ApiTokenRepository tokens;
    @Autowired protected RatingRepository ratings;

    protected User sam;
    protected User alex;
    private long now;

    protected static String M(int i) {
        return String.format("65f0a1b2c3d4e5f6%08d", i);
    }

    @BeforeEach
    void freshData() {
        watchlist.deleteAll();
        ratings.deleteAll();
        tokens.deleteAll();
        users.deleteAll();
        movies.deleteAll();
        WatchlistRateLimiter.reset();
        now = START;
        WatchlistRateLimiter.clock = () -> now;
        for (int i = 0; i < TITLES.length; i++) {
            movies.save(new Movie(M(i + 1), TITLES[i], 2001 + i, "Drama"));
        }
        sam = users.save(new User("Sam Rivera", "sam.rivera@email.com", "x"));
        alex = users.save(new User("Alex Chen", "alex.chen@email.com", "x"));
    }

    /** Moves the clock the rate limiter sees to `seconds` after the start of the test. */
    protected void at(long seconds) {
        now = START + seconds * 1000;
    }

    protected MockHttpServletResponse send(User user, MockHttpServletRequestBuilder request) throws Exception {
        if (user != null) {
            request.header("Authorization", "Bearer " + tokens.save(ApiToken.issue(user.getId())).getToken());
        }
        return mvc.perform(request).andReturn().getResponse();
    }

    protected MockHttpServletResponse get(User user, String url) throws Exception {
        return send(user, MockMvcRequestBuilders.get(url));
    }

    protected MockHttpServletResponse post(User user, String url, String json) throws Exception {
        return send(user, MockMvcRequestBuilders.post(url).contentType(MediaType.APPLICATION_JSON).content(json));
    }

    protected MockHttpServletResponse add(User user, String movieId) throws Exception {
        return post(user, "/api/watchlist/add", movieId == null ? "{}" : "{\"movieId\":\"" + movieId + "\"}");
    }

    protected MockHttpServletResponse remove(User user, String movieId) throws Exception {
        return post(user, "/api/watchlist/remove", movieId == null ? "{}" : "{\"movieId\":\"" + movieId + "\"}");
    }

    protected static JsonNode json(MockHttpServletResponse response) throws Exception {
        return JSON.readTree(response.getContentAsString());
    }

    protected static String message(MockHttpServletResponse response) throws Exception {
        return json(response).path("message").asText(null);
    }

    protected List<String> titles(User user) throws Exception {
        MockHttpServletResponse res = get(user, "/api/watchlist/");
        org.junit.jupiter.api.Assertions.assertEquals(200, res.getStatus(), res.getContentAsString());
        List<String> out = new ArrayList<>();
        json(res).forEach(movie -> out.add(movie.path("title").asText()));
        return out;
    }
}
