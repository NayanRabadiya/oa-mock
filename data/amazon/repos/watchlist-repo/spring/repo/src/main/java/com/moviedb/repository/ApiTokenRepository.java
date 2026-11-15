package com.moviedb.repository;

import com.moviedb.model.ApiToken;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ApiTokenRepository extends JpaRepository<ApiToken, String> {
}
