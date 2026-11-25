package com.desk.seed;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.desk.model.DeskData;
import com.desk.store.DeskStore;
import java.io.InputStream;
import org.springframework.boot.CommandLineRunner;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Component;

/** Loads the sample data in src/main/resources/seed.json when the app starts. */
@Component
public class DataSeeder implements CommandLineRunner {
    private final DeskStore store;
    private final ObjectMapper json;

    public DataSeeder(DeskStore store, ObjectMapper json) {
        this.store = store;
        this.json = json;
    }

    @Override
    public void run(String... args) throws Exception {
        try (InputStream in = new ClassPathResource("seed.json").getInputStream()) {
            store.reset(json.readValue(in, DeskData.class));
        }
    }
}
