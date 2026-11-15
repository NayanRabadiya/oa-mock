package com.moviedb.repository;

import com.moviedb.model.Rating;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface RatingRepository extends JpaRepository<Rating, Long> {
    List<Rating> findByMovieId(String movieId);

    Optional<Rating> findByMovieIdAndUserId(String movieId, Long userId);
}
