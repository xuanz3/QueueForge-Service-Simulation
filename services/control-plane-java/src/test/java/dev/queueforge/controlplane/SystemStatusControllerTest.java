package dev.queueforge.controlplane;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import dev.queueforge.controlplane.run.WorkerSettings;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.jdbc.core.JdbcTemplate;

class SystemStatusControllerTest {
    @TempDir
    Path temporaryDirectory;

    @Test
    void reportsDatabaseAndWorkerReadiness() throws Exception {
        JdbcTemplate jdbc = mock(JdbcTemplate.class);
        when(jdbc.queryForObject("SELECT 1", Integer.class)).thenReturn(1);

        Path worker = temporaryDirectory.resolve("worker");
        Files.writeString(worker, "worker");
        worker.toFile().setExecutable(true);

        WorkerSettings settings = new WorkerSettings(
                temporaryDirectory,
                worker,
                worker,
                "queueforge_analytics",
                worker,
                Duration.ofMinutes(5),
                2);

        Map<String, Object> result = new SystemStatusController(jdbc, settings).status();
        assertEquals("ready", result.get("status"));
        assertEquals("ready", result.get("database"));
    }
}
