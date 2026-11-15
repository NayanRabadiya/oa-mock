package oa.envcheck;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import java.util.Map;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

// A tiny app that uses everything a Spring Boot repository question uses (web, JPA + H2, bcrypt), so setting up the
// environment downloads all of it once. Repositories then run their tests offline.
@SpringBootApplication
public class EnvCheckApplication {
    public static void main(String[] args) {
        SpringApplication.run(EnvCheckApplication.class, args);
    }
}

@Entity
class Thing {
    @Id
    String id;
}

interface ThingRepository extends JpaRepository<Thing, String> {
}

@RestController
class PingController {
    private final ThingRepository things;

    PingController(ThingRepository things) {
        this.things = things;
    }

    @GetMapping("/ping")
    Map<String, Object> ping() {
        return Map.of("ok", new BCryptPasswordEncoder().matches("x", new BCryptPasswordEncoder().encode("x")), "things", things.count());
    }
}
