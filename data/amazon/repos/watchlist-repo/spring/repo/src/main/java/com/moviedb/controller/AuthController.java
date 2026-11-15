package com.moviedb.controller;

import com.moviedb.model.ApiToken;
import com.moviedb.repository.ApiTokenRepository;
import com.moviedb.repository.UserRepository;
import java.util.Map;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/auth")
public class AuthController {
    private static final BCryptPasswordEncoder ENCODER = new BCryptPasswordEncoder();
    private final UserRepository users;
    private final ApiTokenRepository tokens;

    public AuthController(UserRepository users, ApiTokenRepository tokens) {
        this.users = users;
        this.tokens = tokens;
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody Map<String, String> body) {
        String email = String.valueOf(body.getOrDefault("email", "")).trim().toLowerCase();
        var user = users.findByEmail(email);
        if (user.isEmpty() || !ENCODER.matches(String.valueOf(body.getOrDefault("password", "")), user.get().getPassword())) {
            return ResponseEntity.status(401).body(Map.of("message", "Invalid email or password"));
        }
        ApiToken token = tokens.save(ApiToken.issue(user.get().getId()));
        return ResponseEntity.ok(Map.of("token", token.getToken(),
                "user", Map.of("id", user.get().getId(), "name", user.get().getName(), "email", user.get().getEmail())));
    }
}
