package com.moviedb.repository;

import com.moviedb.model.Watchlist;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.transaction.annotation.Transactional;

public interface WatchlistRepository extends JpaRepository<Watchlist, Long> {
    List<Watchlist> findByUserIdOrderByCreatedAtAscIdAsc(Long userId);

    List<Watchlist> findByMovieId(String movieId);

    List<Watchlist> findByUserIdAndMovieId(Long userId, String movieId);

    boolean existsByUserIdAndMovieId(Long userId, String movieId);

    @Transactional
    long deleteByUserIdAndMovieId(Long userId, String movieId);
}
