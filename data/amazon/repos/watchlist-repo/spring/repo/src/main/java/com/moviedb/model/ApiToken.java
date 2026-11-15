package com.moviedb.model;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import java.security.SecureRandom;
import java.util.HexFormat;

// The bearer token a user gets when they log in.
@Entity
public class ApiToken {
    private static final SecureRandom RANDOM = new SecureRandom();

    @Id
    private String token;
    private Long userId;

    protected ApiToken() {
    }

    public ApiToken(String token, Long userId) {
        this.token = token;
        this.userId = userId;
    }

    public static ApiToken issue(Long userId) {
        byte[] b = new byte[24];
        RANDOM.nextBytes(b);
        return new ApiToken(HexFormat.of().formatHex(b), userId);
    }

    public String getToken() { return token; }
    public Long getUserId() { return userId; }
}
