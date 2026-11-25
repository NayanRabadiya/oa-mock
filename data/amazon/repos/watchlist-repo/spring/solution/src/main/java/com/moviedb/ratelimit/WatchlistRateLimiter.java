package com.moviedb.ratelimit;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.LongSupplier;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

/**
 * watchlistRateLimiter: each user may add or remove movies at most 10 times in any 2-minute window.
 * Adds and removes share one counter. It runs before the controller, so every add or remove request it lets
 * through counts, even one that then fails validation. A request it rejects (429) doesn't count.
 */
@Component
public class WatchlistRateLimiter implements HandlerInterceptor {
    private static final long WINDOW_MS = 2 * 60 * 1000;
    private static final int MAX_OPERATIONS = 10;
    private static final Map<Long, List<Long>> STORE = new ConcurrentHashMap<>();

    // The limiter reads the time from here, so the tests can move it.
    public static LongSupplier clock = System::currentTimeMillis;

    public static void reset() {
        STORE.clear();
    }

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        Long userId = (Long) request.getAttribute("userId");
        if (userId == null) {
            response.setStatus(401);
            response.setContentType("application/json");
            response.getWriter().write("{\"message\":\"Unauthorized\"}");
            return false;
        }
        long now = clock.getAsLong();
        synchronized (STORE) {
            List<Long> history = STORE.getOrDefault(userId, new ArrayList<>());
            List<Long> recent = new ArrayList<>();
            for (long stamp : history) {
                if (now - stamp < WINDOW_MS) {
                    recent.add(stamp);
                }
            }
            if (recent.size() >= MAX_OPERATIONS) {
                STORE.put(userId, recent);
                response.setStatus(429);
                response.setContentType("application/json");
                response.getWriter().write("{\"message\":\"Too many watchlist operations. You can add or remove movies up to 10 times within 2 minutes.\"}");
                return false;
            }
            recent.add(now);
            STORE.put(userId, recent);
        }
        return true;
    }
}
