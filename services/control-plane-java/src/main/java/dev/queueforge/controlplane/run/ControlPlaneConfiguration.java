package dev.queueforge.controlplane.run;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class ControlPlaneConfiguration {

    @Bean
    WorkerSettings workerSettings(
            @Value("${queueforge.work-root:/var/lib/queueforge/runs}") Path workRoot,
            @Value("${queueforge.workers.simulation-command:/usr/local/bin/queueforge-sim}") Path simulationCommand,
            @Value("${queueforge.workers.analytics-python:/usr/local/bin/python}") Path analyticsPython,
            @Value("${queueforge.workers.analytics-module:queueforge_analytics}") String analyticsModule,
            @Value("${queueforge.workers.analytics-engine:/usr/local/bin/queueforge-sim}") Path analyticsEngine,
            @Value("${queueforge.workers.timeout:PT5M}") Duration timeout,
            @Value("${queueforge.workers.max-concurrency:2}") int maxConcurrency) throws IOException {
        if (maxConcurrency < 1 || maxConcurrency > 8) {
            throw new IllegalArgumentException("queueforge.workers.max-concurrency must be between 1 and 8");
        }
        Files.createDirectories(workRoot);
        return new WorkerSettings(
                workRoot,
                simulationCommand,
                analyticsPython,
                analyticsModule,
                analyticsEngine,
                timeout,
                maxConcurrency);
    }

    @Bean(destroyMethod = "shutdown")
    ExecutorService runExecutor(WorkerSettings settings) {
        return Executors.newFixedThreadPool(settings.maxConcurrency(), Thread.ofPlatform()
                .name("queueforge-run-", 0)
                .factory());
    }
}
