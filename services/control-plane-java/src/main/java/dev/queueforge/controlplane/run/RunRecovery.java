package dev.queueforge.controlplane.run;

import java.time.Instant;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

@Component
public class RunRecovery implements ApplicationRunner {
    private final RunRepository repository;
    private final RunTelemetry telemetry;

    public RunRecovery(RunRepository repository, RunTelemetry telemetry) {
        this.repository = repository;
        this.telemetry = telemetry;
    }

    @Override
    public void run(ApplicationArguments args) {
        int recovered = repository.failIncompleteRuns(Instant.now());
        telemetry.recovered(recovered);
    }
}
