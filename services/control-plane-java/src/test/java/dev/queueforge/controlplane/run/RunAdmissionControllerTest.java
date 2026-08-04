package dev.queueforge.controlplane.run;

import static org.assertj.core.api.Assertions.assertThat;

import java.nio.file.Path;
import java.time.Duration;
import org.junit.jupiter.api.Test;

class RunAdmissionControllerTest {

    @Test
    void boundsConcurrentAndQueuedRuns() {
        RunAdmissionController admission = new RunAdmissionController(settings());

        assertThat(admission.tryAcquire()).isTrue();
        assertThat(admission.tryAcquire()).isTrue();
        assertThat(admission.tryAcquire()).isTrue();
        assertThat(admission.tryAcquire()).isFalse();
        assertThat(admission.snapshot())
                .isEqualTo(new RunAdmissionController.Snapshot(3, 3, 0));

        admission.release();

        assertThat(admission.tryAcquire()).isTrue();
        assertThat(admission.snapshot().admitted()).isEqualTo(3);
    }

    private static WorkerSettings settings() {
        return new WorkerSettings(
                Path.of("/work"),
                Path.of("/worker"),
                Path.of("/python"),
                "queueforge_analytics",
                Path.of("/engine"),
                Duration.ofMinutes(5),
                2,
                1);
    }
}
