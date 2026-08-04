package dev.queueforge.controlplane.run;

import java.nio.file.Path;
import java.time.Duration;

public record WorkerSettings(
        Path workRoot,
        Path simulationCommand,
        Path analyticsPython,
        String analyticsModule,
        Path analyticsEngine,
        Duration timeout,
        int maxConcurrency) {
}
