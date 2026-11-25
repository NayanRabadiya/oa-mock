package com.moviedb.config;

import com.moviedb.ratelimit.WatchlistRateLimiter;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

// The routes the watchlist rate limiter guards.
@Configuration
public class WebConfig implements WebMvcConfigurer {
    private final WatchlistRateLimiter watchlistRateLimiter;

    public WebConfig(WatchlistRateLimiter watchlistRateLimiter) {
        this.watchlistRateLimiter = watchlistRateLimiter;
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(watchlistRateLimiter)
                .addPathPatterns("/api/watchlist/add", "/api/watchlist/remove/");
    }
}
