package dev.queueforge.controlplane;

import dev.queueforge.controlplane.run.WorkerSettings;
import java.nio.file.Files;
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
    private final WorkerSettings workers;

    public SystemStatusController(JdbcTemplate jdbc, WorkerSettings workers) {
        this.jdbc = jdbc;
        this.workers = workers;
    }

    @GetMapping("/status")
    public Map<String, Object> status() {
        Integer probe = jdbc.queryForObject("SELECT 1", Integer.class);
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("service", "queueforge-control-plane");
        result.put("version", "0.4.0");
        result.put("status", "ready");
        result.put("database", probe != null && probe == 1 ? "ready" : "unavailable");
        result.put("workers", Map.of(
                "simulation", executable(workers.simulationCommand()),
                "analytics", executable(workers.analyticsPython()),
                "analyticsEngine", executable(workers.analyticsEngine())));
        result.put("workRoot", Files.isWritable(workers.workRoot()) ? "ready" : "unavailable");
        result.put("checkedAt", Instant.now().toString());
        return result;
    }

    private static String executable(java.nio.file.Path path) {
        return Files.isExecutable(path) ? "ready" : "unavailable";
    }
}
