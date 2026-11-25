package com.moviedb.security;

import com.moviedb.repository.ApiTokenRepository;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

// authMiddleware: reads `Authorization: Bearer <token>` and sets the request attribute "userId", or answers 401.
@Component
public class AuthFilter extends OncePerRequestFilter {
    private final ApiTokenRepository tokens;

    public AuthFilter(ApiTokenRepository tokens) {
        this.tokens = tokens;
    }

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        String path = request.getRequestURI();
        return !path.startsWith("/api/") || path.startsWith("/api/auth/");
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        String header = request.getHeader("Authorization");
        if (header != null && header.startsWith("Bearer ")) {
            var token = tokens.findById(header.substring(7).trim());
            if (token.isPresent()) {
                request.setAttribute("userId", token.get().getUserId());
                chain.doFilter(request, response);
                return;
            }
        }
        response.setStatus(401);
        response.setContentType("application/json");
        response.getWriter().write("{\"message\":\"Unauthorized\"}");
    }
}
