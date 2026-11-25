package oa.envcheck;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;

@SpringBootTest
@AutoConfigureMockMvc
class EnvCheckTests {
    @Autowired
    MockMvc mvc;

    @Test
    void pingAnswers() throws Exception {
        assertEquals(200, mvc.perform(MockMvcRequestBuilders.get("/ping")).andReturn().getResponse().getStatus());
    }
}
