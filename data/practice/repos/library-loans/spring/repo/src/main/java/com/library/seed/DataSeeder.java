package com.library.seed;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.library.model.LibraryData;
import com.library.store.LibraryStore;
import java.io.InputStream;
import org.springframework.boot.CommandLineRunner;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Component;

/** Loads the sample data in src/main/resources/seed.json when the app starts. */
@Component
public class DataSeeder implements CommandLineRunner {
    private final LibraryStore store;
    private final ObjectMapper json;

    public DataSeeder(LibraryStore store, ObjectMapper json) {
        this.store = store;
        this.json = json;
    }

    @Override
    public void run(String... args) throws Exception {
        try (InputStream in = new ClassPathResource("seed.json").getInputStream()) {
            store.reset(json.readValue(in, LibraryData.class));
        }
    }
}
