package com.moviedb.seed;

import com.moviedb.model.Movie;
import com.moviedb.model.User;
import com.moviedb.repository.MovieRepository;
import com.moviedb.repository.UserRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Component;

// Adds the sample movies and the two test users from the README when the app starts with an empty database.
@Component
public class DataSeeder implements CommandLineRunner {
    private static final String[] TITLES = {"The Shawshank Redemption", "Interstellar", "The Dark Knight",
            "Spirited Away", "Parasite", "Inception"};
    private static final int[] YEARS = {1994, 2014, 2008, 2001, 2019, 2010};
    private static final String[] GENRES = {"Drama", "Sci-Fi", "Action", "Animation", "Thriller", "Sci-Fi"};

    private final MovieRepository movies;
    private final UserRepository users;

    public DataSeeder(MovieRepository movies, UserRepository users) {
        this.movies = movies;
        this.users = users;
    }

    @Override
    public void run(String... args) {
        if (movies.count() > 0) {
            return;
        }
        for (int i = 0; i < TITLES.length; i++) {
            movies.save(new Movie(String.format("65f0a1b2c3d4e5f6%08d", i + 1), TITLES[i], YEARS[i], GENRES[i]));
        }
        String password = new BCryptPasswordEncoder().encode("Password@123");
        users.save(new User("Sam Rivera", "sam.rivera@email.com", password));
        users.save(new User("Alex Chen", "alex.chen@email.com", password));
    }
}
