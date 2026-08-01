package dev.queueforge.controlplane;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.springframework.jdbc.core.JdbcTemplate;
class SystemStatusControllerTest {
    @Test void reportsDatabaseReadiness() {
        JdbcTemplate jdbc = mock(JdbcTemplate.class);
        when(jdbc.queryForObject("SELECT 1", Integer.class)).thenReturn(1);
        Map<String, Object> result = new SystemStatusController(jdbc).status();
        assertEquals("ready", result.get("status"));
        assertEquals("ready", result.get("database"));
    }
}
