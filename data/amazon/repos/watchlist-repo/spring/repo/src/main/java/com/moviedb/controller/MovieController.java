package com.moviedb.controller;

import com.moviedb.config.ObjectIds;
import com.moviedb.model.Rating;
import com.moviedb.repository.MovieRepository;
import com.moviedb.repository.RatingRepository;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.springframework.data.domain.Sort;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestAttribute;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/movies")
public class MovieController {
    private final MovieRepository movies;
    private final RatingRepository ratings;

    public MovieController(MovieRepository movies, RatingRepository ratings) {
        this.movies = movies;
        this.ratings = ratings;
    }

    @GetMapping("/")
    public ResponseEntity<?> listMovies() {
        return ResponseEntity.ok(movies.findAll(Sort.by("title")));
    }

    @GetMapping("/{movieId}")
    public ResponseEntity<?> getMovie(@PathVariable("movieId") String movieId) {
        if (!ObjectIds.isValid(movieId)) {
            return ResponseEntity.status(400).body(Map.of("message", "Invalid movie ID format"));
        }
        var movie = movies.findById(movieId);
        if (movie.isEmpty()) {
            return ResponseEntity.status(404).body(Map.of("message", "Movie not found"));
        }
        List<Rating> all = ratings.findByMovieId(movieId);
        int total = all.stream().mapToInt(Rating::getStars).sum();
        Map<String, Object> out = new LinkedHashMap<>();
        out.put("id", movie.get().getId());
        out.put("title", movie.get().getTitle());
        out.put("year", movie.get().getYear());
        out.put("genre", movie.get().getGenre());
        out.put("averageRating", all.isEmpty() ? null : total / all.size());
        out.put("ratingsCount", all.size());
        return ResponseEntity.ok(out);
    }

    @PostMapping("/{movieId}/rate")
    public ResponseEntity<?> rateMovie(@RequestAttribute("userId") Long userId, @PathVariable("movieId") String movieId,
                                       @RequestBody Map<String, Object> body) {
        Object stars = body.get("stars");
        if (!(stars instanceof Integer s) || s < 1 || s > 5) {
            return ResponseEntity.status(400).body(Map.of("message", "Stars must be a whole number from 1 to 5"));
        }
        var movie = movies.findById(movieId);
        if (movie.isEmpty()) {
            return ResponseEntity.status(404).body(Map.of("message", "Movie not found"));
        }
        Rating rating = ratings.findByMovieIdAndUserId(movieId, userId)
                .orElse(new Rating(movie.get(), userId, s, ""));
        rating.setStars(s);
        rating.setReview(String.valueOf(body.getOrDefault("review", "")));
        ratings.save(rating);
        return ResponseEntity.status(201).body(Map.of("message", "Rating saved"));
    }
}
