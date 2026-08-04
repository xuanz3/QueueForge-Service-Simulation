package dev.queueforge.controlplane.run;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.Test;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;
import tools.jackson.databind.json.JsonMapper;

class RunServiceContextTest {

    @Test
    void springSelectsTheProductionInjectionConstructor() {
        ExecutorService executor = Executors.newSingleThreadExecutor();

        try (AnnotationConfigApplicationContext context =
                new AnnotationConfigApplicationContext()) {
            context.registerBean(RunRepository.class, () -> mock(RunRepository.class));
            context.registerBean(ScenarioValidator.class, () -> mock(ScenarioValidator.class));
            context.registerBean(WorkerProcessRunner.class, () -> mock(WorkerProcessRunner.class));
            context.registerBean(JsonMapper.class, () -> mock(JsonMapper.class));
            context.registerBean(ExecutorService.class, () -> executor);
            context.registerBean(
                    RunAdmissionController.class,
                    () -> mock(RunAdmissionController.class));
            context.registerBean(RunTelemetry.class, () -> mock(RunTelemetry.class));
            context.registerBean(RunService.class);

            context.refresh();

            assertThat(context.getBean(RunService.class)).isNotNull();
        } finally {
            executor.shutdownNow();
        }
    }
}
