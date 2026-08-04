package dev.queueforge.controlplane.run;

import java.time.Clock;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import tools.jackson.databind.json.JsonMapper;

@Service
public class RunService {
    private final RunRepository repository;
    private final ScenarioValidator validator;
    private final WorkerProcessRunner workerRunner;
    private final JsonMapper jsonMapper;
    private final ExecutorService executor;
    private final Clock clock;

    @Autowired
    public RunService(
            RunRepository repository,
            ScenarioValidator validator,
            WorkerProcessRunner workerRunner,
            JsonMapper jsonMapper,
            ExecutorService executor) {
        this(repository, validator, workerRunner, jsonMapper, executor, Clock.systemUTC());
    }

    RunService(
            RunRepository repository,
            ScenarioValidator validator,
            WorkerProcessRunner workerRunner,
            JsonMapper jsonMapper,
            ExecutorService executor,
            Clock clock) {
        this.repository = repository;
        this.validator = validator;
        this.workerRunner = workerRunner;
        this.jsonMapper = jsonMapper;
        this.executor = executor;
        this.clock = clock;
    }

    public RunRecord submit(CreateRunRequest request) {
        NormalizedRunRequest normalized = validator.normalize(request);
        UUID id = UUID.randomUUID();
        Instant createdAt = clock.instant();
        repository.insert(id, normalized.type(), writeJson(normalized), createdAt);
        executor.execute(() -> execute(id, normalized));
        return get(id);
    }

    public RunRecord get(UUID id) {
        return repository.find(id).orElseThrow(() -> new RunNotFoundException(id));
    }

    public List<RunRecord> list(int limit) {
        if (limit < 1 || limit > 200) {
            throw new InvalidRunRequestException("limit must be between 1 and 200");
        }
        return repository.findRecent(limit);
    }

    public RunRecord cancel(UUID id) {
        RunRecord current = get(id);
        if (current.status().isTerminal()) {
            return current;
        }

        repository.requestCancellation(id);
        workerRunner.cancel(id);
        repository.markCancelled(id, clock.instant());
        return get(id);
    }

    public String result(UUID id) {
        RunRecord run = get(id);
        if (run.status() != RunStatus.SUCCEEDED || run.resultJson() == null) {
            throw new RunConflictException(
                    "Run result is unavailable while status is " + run.status());
        }
        return run.resultJson();
    }

    private void execute(UUID id, NormalizedRunRequest request) {
        if (!repository.markRunning(id, clock.instant())) {
            return;
        }
        try {
            String result = workerRunner.execute(
                    id,
                    request,
                    () -> repository.isCancellationRequested(id),
                    processId -> repository.setProcessId(id, processId));
            if (repository.isCancellationRequested(id)) {
                repository.markCancelled(id, clock.instant());
            } else {
                repository.markSucceeded(id, result, clock.instant());
            }
        } catch (WorkerCancelledException exception) {
            repository.markCancelled(id, clock.instant());
        } catch (WorkerExecutionException exception) {
            repository.markFailed(id, exception.code(), exception.getMessage(), clock.instant());
        } catch (RuntimeException exception) {
            repository.markFailed(id, "CONTROL_PLANE_ERROR", exception.getMessage(), clock.instant());
        }
    }

    private String writeJson(Object value) {
        try {
            return jsonMapper.writeValueAsString(value);
        } catch (Exception exception) {
            throw new InvalidRunRequestException("Unable to serialize run request: " + exception.getMessage());
        }
    }
}
