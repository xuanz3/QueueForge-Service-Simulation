package dev.queueforge.controlplane.run;

import java.time.Instant;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

@Component
public class RunRecovery implements ApplicationRunner {
    private final RunRepository repository;

    public RunRecovery(RunRepository repository) {
        this.repository = repository;
    }

    @Override
    public void run(ApplicationArguments args) {
        repository.failIncompleteRuns(Instant.now());
    }
}
