package com.moviedb.controller;

import com.moviedb.config.ObjectIds;
import com.moviedb.model.Movie;
import com.moviedb.model.Watchlist;
import com.moviedb.repository.MovieRepository;
import com.moviedb.repository.WatchlistRepository;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestAttribute;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/watchlist")
public class WatchlistController {
    private static final Logger log = LoggerFactory.getLogger(WatchlistController.class);

    private final WatchlistRepository watchlistRepository;
    private final MovieRepository movieRepository;

    public WatchlistController(WatchlistRepository watchlistRepository, MovieRepository movieRepository) {
        this.watchlistRepository = watchlistRepository;
        this.movieRepository = movieRepository;
    }

    private static ResponseEntity<Map<String, String>> error(int status, String message) {
        return ResponseEntity.status(status).body(Map.of("message", message));
    }

    private static String movieIdOf(Map<String, Object> body) {
        Object raw = body == null ? null : body.get("movieId");
        return raw == null ? null : raw.toString();
    }

    @GetMapping("/")
    public ResponseEntity<?> getWatchlist(@RequestAttribute("userId") Long userId) {
        try {
            List<Watchlist> entries = watchlistRepository.findByUserIdOrderByCreatedAtAscIdAsc(userId);

            List<Movie> movies = entries.stream().map(Watchlist::getMovie).toList();

            return ResponseEntity.ok(movies);
        } catch (Exception e) {
            log.error("Get watchlist error", e);
            return error(500, "Server error");
        }
    }

    @PostMapping("/add")
    public ResponseEntity<?> addToWatchlist(@RequestAttribute("userId") Long userId,
                                            @RequestBody(required = false) Map<String, Object> body) {
        try {
            String movieId = movieIdOf(body);
            if (movieId == null || movieId.isEmpty()) {
                return error(400, "Movie ID is required");
            }
            if (!ObjectIds.isValid(movieId)) {
                return error(400, "Invalid movie ID format");
            }
            Optional<Movie> movie = movieRepository.findById(movieId);
            if (movie.isEmpty()) {
                return error(404, "Movie not found");
            }

            if (watchlistRepository.existsByUserIdAndMovieId(userId, movieId)) {
                return error(400, "Movie already in watchlist");
            }
            watchlistRepository.save(new Watchlist(userId, movie.get()));

            return ResponseEntity.status(201).body(Map.of("message", "Movie added to watchlist successfully"));
        } catch (DataIntegrityViolationException e) {
            // the unique constraint is a second safety net against duplicates
            return error(400, "Movie already in watchlist");
        } catch (Exception e) {
            log.error("Add to watchlist error", e);
            return error(500, "Server error");
        }
    }

    @PostMapping("/remove")
    public ResponseEntity<?> removeFromWatchlist(@RequestAttribute("userId") Long userId,
                                                 @RequestBody(required = false) Map<String, Object> body) {
        try {
            String movieId = movieIdOf(body);
            if (movieId == null || movieId.isEmpty()) {
                return error(400, "Movie ID is required");
            }
            if (!ObjectIds.isValid(movieId)) {
                return error(400, "Invalid movie ID format");
            }

            long deleted = watchlistRepository.deleteByUserIdAndMovieId(userId, movieId);
            if (deleted == 0) {
                return error(404, "Movie not found in watchlist");
            }

            return ResponseEntity.ok(Map.of("message", "Movie removed from watchlist successfully"));
        } catch (Exception e) {
            log.error("Remove from watchlist error", e);
            return error(500, "Server error");
        }
    }

    @GetMapping("/check/{movieId}")
    public ResponseEntity<?> checkWatchlistStatus(@RequestAttribute("userId") Long userId,
                                                  @PathVariable("movieId") String movieId) {
        try {
            if (!ObjectIds.isValid(movieId)) {
                return error(400, "Invalid movie ID format");
            }

            boolean inWatchlist = watchlistRepository.existsByUserIdAndMovieId(userId, movieId);

            return ResponseEntity.ok(Map.of("isInWatchlist", inWatchlist));
        } catch (Exception e) {
            log.error("Check watchlist status error", e);
            return error(500, "Server error");
        }
    }
}
