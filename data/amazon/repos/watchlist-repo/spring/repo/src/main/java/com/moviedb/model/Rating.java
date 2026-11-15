package com.moviedb.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;

@Entity
@Table(uniqueConstraints = @UniqueConstraint(columnNames = {"movie_id", "user_id"}))
public class Rating {
    @Id
    @GeneratedValue
    private Long id;
    @ManyToOne
    private Movie movie;
    @Column(name = "user_id")
    private Long userId;
    private int stars;
    private String review;

    protected Rating() {
    }

    public Rating(Movie movie, Long userId, int stars, String review) {
        this.movie = movie;
        this.userId = userId;
        this.stars = stars;
        this.review = review;
    }

    public int getStars() { return stars; }
    public void setStars(int stars) { this.stars = stars; }
    public void setReview(String review) { this.review = review; }
}
