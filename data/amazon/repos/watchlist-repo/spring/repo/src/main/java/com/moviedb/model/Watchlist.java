package com.moviedb.model;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import java.time.Instant;

// One saved movie on one user's watchlist.
@Entity
@Table(uniqueConstraints = @UniqueConstraint(columnNames = {"user_id", "movie_id"}))
public class Watchlist {
    @Id
    @GeneratedValue
    private Long id;
    @Column(name = "user_id", nullable = false)
    private Long userId;
    @ManyToOne(fetch = FetchType.EAGER, optional = false)
    private Movie movie;
    @JsonIgnore
    private Instant createdAt;

    protected Watchlist() {
    }

    public Watchlist(Long userId, Movie movie) {
        this.userId = userId;
        this.movie = movie;
    }

    @PrePersist
    void onCreate() {
        createdAt = Instant.now();
    }

    public Long getId() { return id; }
    public Long getUserId() { return userId; }
    public Movie getMovie() { return movie; }
    public Instant getCreatedAt() { return createdAt; }
}
