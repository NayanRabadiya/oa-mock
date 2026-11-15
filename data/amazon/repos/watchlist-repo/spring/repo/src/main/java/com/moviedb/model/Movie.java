package com.moviedb.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;

// Ids look like MongoDB ObjectIds (24 hex characters), as in the rest of the MovieDB platform.
@Entity
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class Movie {
    @Id
    private String id;
    private String title;
    @Column(name = "release_year")
    private int year;
    private String genre;

    protected Movie() {
    }

    public Movie(String id, String title, int year, String genre) {
        this.id = id;
        this.title = title;
        this.year = year;
        this.genre = genre;
    }

    public String getId() { return id; }
    public String getTitle() { return title; }
    public int getYear() { return year; }
    public String getGenre() { return genre; }
}
