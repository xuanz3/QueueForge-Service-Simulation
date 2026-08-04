package dev.queueforge.controlplane;

import dev.queueforge.controlplane.run.RunAdmissionController;
import dev.queueforge.controlplane.run.WorkerSettings;
import java.nio.file.Files;
import java.util.LinkedHashMap;
import java.util.Map;
import org.springframework.boot.health.contributor.Health;
import org.springframework.boot.health.contributor.HealthIndicator;
import org.springframework.stereotype.Component;

@Component("queueforgeWorkers")
public class WorkerReadinessHealthIndicator implements HealthIndicator {
    private final WorkerSettings workers;
    private final RunAdmissionController admission;

    public WorkerReadinessHealthIndicator(
            WorkerSettings workers,
            RunAdmissionController admission) {
        this.workers = workers;
        this.admission = admission;
    }

    @Override
    public Health health() {
        Map<String, Object> details = new LinkedHashMap<>();
        details.put("simulation", executable(workers.simulationCommand()));
        details.put("analytics", executable(workers.analyticsPython()));
        details.put("analyticsEngine", executable(workers.analyticsEngine()));
        details.put("workRootWritable", Files.isWritable(workers.workRoot()));
        details.put("capacity", admission.snapshot());

        boolean ready = Boolean.TRUE.equals(details.get("simulation"))
                && Boolean.TRUE.equals(details.get("analytics"))
                && Boolean.TRUE.equals(details.get("analyticsEngine"))
                && Boolean.TRUE.equals(details.get("workRootWritable"));

        Health.Builder builder = ready ? Health.up() : Health.down();
        return builder.withDetails(details).build();
    }

    private static boolean executable(java.nio.file.Path path) {
        return Files.isExecutable(path);
    }
}
