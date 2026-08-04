package dev.queueforge.controlplane.run;

import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import org.springframework.stereotype.Component;

@Component
public class WorkerCommandFactory {
    private final WorkerSettings settings;

    public WorkerCommandFactory(WorkerSettings settings) {
        this.settings = settings;
    }

    WorkerPlan create(NormalizedRunRequest request, Path workDirectory) {
        Path input = workDirectory.resolve("request.json");
        Path stdout = workDirectory.resolve("stdout.log");
        Path stderr = workDirectory.resolve("stderr.log");

        if (request.type() == RunType.SIMULATION) {
            Path result = workDirectory.resolve("simulation-result.json");
            return new WorkerPlan(
                    List.of(
                            settings.simulationCommand().toString(),
                            "--input", input.toString(),
                            "--output", result.toString(),
                            "--pretty"),
                    result,
                    stdout,
                    stderr);
        }

        Path reports = workDirectory.resolve("reports");
        List<String> command = new ArrayList<>();
        command.add(settings.analyticsPython().toString());
        command.add("-m");
        command.add(settings.analyticsModule());
        command.add("experiment");
        command.add("--scenario");
        command.add(input.toString());
        command.add("--output-dir");
        command.add(reports.toString());
        command.add("--server-counts");
        command.add(request.serverCounts().stream()
                .map(String::valueOf)
                .collect(Collectors.joining(",")));
        command.add("--runs");
        command.add(String.valueOf(request.runs()));
        command.add("--seed-start");
        command.add(String.valueOf(request.seedStart()));
        command.add("--target-p95-wait");
        command.add(String.valueOf(request.targetP95Wait()));
        command.add("--target-max-queue");
        command.add(String.valueOf(request.targetMaxQueue()));
        command.add("--target-max-utilisation");
        command.add(String.valueOf(request.targetMaxUtilisation()));
        command.add("--required-success-rate");
        command.add(String.valueOf(request.requiredSuccessRate()));
        command.add("--engine");
        command.add(settings.analyticsEngine().toString());

        return new WorkerPlan(
                List.copyOf(command),
                reports.resolve("staffing-comparison.json"),
                stdout,
                stderr);
    }
}
