package dev.queueforge.controlplane;
import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
@RestController
@RequestMapping("/api/system")
public class SystemStatusController {
    private final JdbcTemplate jdbc;
    public SystemStatusController(JdbcTemplate jdbc) { this.jdbc = jdbc; }
    @GetMapping("/status")
    public Map<String, Object> status() {
        Integer probe = jdbc.queryForObject("SELECT 1", Integer.class);
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("service", "queueforge-control-plane");
        result.put("version", "0.1.0");
        result.put("status", "ready");
        result.put("database", probe != null && probe == 1 ? "ready" : "unavailable");
        result.put("checkedAt", Instant.now().toString());
        return result;
    }
}
