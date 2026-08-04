package dev.queueforge.controlplane;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import dev.queueforge.controlplane.run.RunAdmissionController;
import dev.queueforge.controlplane.run.RunTelemetry;
import dev.queueforge.controlplane.run.WorkerSettings;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
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
    void reportsDatabaseWorkerAndCapacityReadiness() throws Exception {
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
                2,
                4);
        RunAdmissionController admission = new RunAdmissionController(settings);
        RunTelemetry telemetry = new RunTelemetry(new SimpleMeterRegistry());

        Map<String, Object> result =
                new SystemStatusController(jdbc, settings, admission, telemetry).status();

        assertEquals("ready", result.get("status"));
        assertEquals("ready", result.get("database"));
        assertEquals("0.6.0", result.get("version"));
        assertEquals(admission.snapshot(), result.get("capacity"));
    }
}
