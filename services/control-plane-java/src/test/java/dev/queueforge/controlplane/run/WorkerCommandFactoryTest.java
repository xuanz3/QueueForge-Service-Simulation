package dev.queueforge.controlplane.run;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.file.Path;
import java.time.Duration;
import java.util.List;
import org.junit.jupiter.api.Test;

class WorkerCommandFactoryTest {
    private final WorkerSettings settings = new WorkerSettings(
            Path.of("/work"),
            Path.of("/bin/queueforge-sim"),
            Path.of("/bin/python"),
            "queueforge_analytics",
            Path.of("/bin/queueforge-sim"),
            Duration.ofMinutes(5),
            2);

    @Test
    void createsSimulationCommandWithoutShellInterpolation() {
        WorkerPlan plan = new WorkerCommandFactory(settings).create(
                new NormalizedRunRequest(
                        RunType.SIMULATION,
                        ScenarioValidatorTest.scenario(),
                        List.of(),
                        1,
                        20260801L,
                        10,
                        20,
                        0.85,
                        0.90),
                Path.of("/tmp/run"));

        assertEquals("/bin/queueforge-sim", plan.command().getFirst());
        assertTrue(plan.command().contains("--pretty"));
        assertEquals(Path.of("/tmp/run/simulation-result.json"), plan.resultPath());
    }

    @Test
    void createsAnalyticsCommandWithExplicitEnginePath() {
        WorkerPlan plan = new WorkerCommandFactory(settings).create(
                new NormalizedRunRequest(
                        RunType.ANALYTICS,
                        ScenarioValidatorTest.scenario(),
                        List.of(3, 4, 5),
                        40,
                        20260801L,
                        10,
                        20,
                        0.85,
                        0.90),
                Path.of("/tmp/run"));

        assertTrue(plan.command().contains("queueforge_analytics"));
        assertTrue(plan.command().contains("3,4,5"));
        assertTrue(plan.command().contains("/bin/queueforge-sim"));
    }
}
