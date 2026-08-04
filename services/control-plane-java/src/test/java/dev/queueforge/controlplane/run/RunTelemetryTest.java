package dev.queueforge.controlplane.run;

import static org.assertj.core.api.Assertions.assertThat;

import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import org.junit.jupiter.api.Test;

class RunTelemetryTest {

    @Test
    void recordsAdmissionAndTerminalOutcomes() {
        RunTelemetry telemetry = new RunTelemetry(new SimpleMeterRegistry());

        telemetry.submitted();
        telemetry.rejected();
        telemetry.started();
        telemetry.completed(RunStatus.SUCCEEDED, System.nanoTime());
        telemetry.recovered(2);

        assertThat(telemetry.snapshot())
                .containsEntry("active", 0)
                .containsEntry("submitted", 1.0)
                .containsEntry("rejected", 1.0)
                .containsEntry("succeeded", 1.0)
                .containsEntry("recovered", 2.0);
    }
}
