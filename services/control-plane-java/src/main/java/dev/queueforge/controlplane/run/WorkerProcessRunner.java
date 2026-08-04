package dev.queueforge.controlplane.run;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeUnit;
import java.util.function.BooleanSupplier;
import java.util.function.LongConsumer;
import org.springframework.stereotype.Component;
import tools.jackson.databind.json.JsonMapper;

@Component
public class WorkerProcessRunner {
    private static final int MAX_ERROR_CHARACTERS = 4000;

    private final WorkerSettings settings;
    private final WorkerCommandFactory commandFactory;
    private final JsonMapper jsonMapper;
    private final ConcurrentHashMap<UUID, Process> activeProcesses = new ConcurrentHashMap<>();

    public WorkerProcessRunner(
            WorkerSettings settings,
            WorkerCommandFactory commandFactory,
            JsonMapper jsonMapper) {
        this.settings = settings;
        this.commandFactory = commandFactory;
        this.jsonMapper = jsonMapper;
    }

    public String execute(
            UUID runId,
            NormalizedRunRequest request,
            BooleanSupplier cancellationRequested,
            LongConsumer processStarted) {
        Path workDirectory = settings.workRoot().resolve(runId.toString());
        try {
            Files.createDirectories(workDirectory);
            jsonMapper.writeValue(workDirectory.resolve("request.json").toFile(), request.scenario());
            WorkerPlan plan = commandFactory.create(request, workDirectory);
            Files.createDirectories(plan.resultPath().getParent());

            Process process = new ProcessBuilder(plan.command())
                    .directory(workDirectory.toFile())
                    .redirectOutput(plan.stdoutPath().toFile())
                    .redirectError(plan.stderrPath().toFile())
                    .start();

            activeProcesses.put(runId, process);
            processStarted.accept(process.pid());
            waitForCompletion(process, cancellationRequested, settings.timeout());

            if (cancellationRequested.getAsBoolean()) {
                throw new WorkerCancelledException();
            }
            if (process.exitValue() != 0) {
                throw new WorkerExecutionException(
                        "WORKER_EXIT_" + process.exitValue(),
                        readError(plan.stderrPath(), "Worker exited with code " + process.exitValue()));
            }
            if (!Files.isRegularFile(plan.resultPath())) {
                throw new WorkerExecutionException(
                        "WORKER_RESULT_MISSING",
                        "Worker completed without creating " + plan.resultPath().getFileName());
            }

            String resultJson = Files.readString(plan.resultPath(), StandardCharsets.UTF_8);
            jsonMapper.readValue(resultJson, Object.class);
            return resultJson;
        } catch (WorkerCancelledException | WorkerExecutionException exception) {
            throw exception;
        } catch (IOException exception) {
            throw new WorkerExecutionException("WORKER_IO", exception.getMessage(), exception);
        } finally {
            activeProcesses.remove(runId);
        }
    }

    public boolean cancel(UUID runId) {
        Process process = activeProcesses.get(runId);
        if (process == null) {
            return false;
        }
        terminate(process);
        return true;
    }

    private static void waitForCompletion(
            Process process,
            BooleanSupplier cancellationRequested,
            Duration timeout) {
        long deadline = System.nanoTime() + timeout.toNanos();
        try {
            while (process.isAlive()) {
                if (cancellationRequested.getAsBoolean()) {
                    terminate(process);
                    throw new WorkerCancelledException();
                }
                if (System.nanoTime() >= deadline) {
                    terminate(process);
                    throw new WorkerExecutionException(
                            "WORKER_TIMEOUT",
                            "Worker exceeded timeout " + timeout);
                }
                process.waitFor(200, TimeUnit.MILLISECONDS);
            }
        } catch (InterruptedException exception) {
            Thread.currentThread().interrupt();
            terminate(process);
            throw new WorkerExecutionException(
                    "WORKER_INTERRUPTED",
                    "Worker thread was interrupted",
                    exception);
        }
    }

    private static void terminate(Process process) {
        process.descendants().forEach(ProcessHandle::destroy);
        process.destroy();
        try {
            if (!process.waitFor(2, TimeUnit.SECONDS)) {
                process.descendants().forEach(ProcessHandle::destroyForcibly);
                process.destroyForcibly();
            }
        } catch (InterruptedException exception) {
            Thread.currentThread().interrupt();
            process.destroyForcibly();
        }
    }

    private static String readError(Path path, String fallback) {
        try {
            if (!Files.isRegularFile(path)) {
                return fallback;
            }
            String text = Files.readString(path, StandardCharsets.UTF_8).strip();
            if (text.isEmpty()) {
                return fallback;
            }
            return text.length() <= MAX_ERROR_CHARACTERS
                    ? text
                    : text.substring(0, MAX_ERROR_CHARACTERS);
        } catch (IOException ignored) {
            return fallback;
        }
    }
}
