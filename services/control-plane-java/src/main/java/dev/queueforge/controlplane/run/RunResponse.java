package dev.queueforge.controlplane.run;

import java.time.Instant;
import java.util.Map;
import java.util.UUID;

public record RunResponse(
        UUID id,
        RunType type,
        RunStatus status,
        Long processId,
        Instant createdAt,
        Instant startedAt,
        Instant completedAt,
        boolean cancelRequested,
        String errorCode,
        String errorMessage,
        Map<String, String> links) {

    public static RunResponse from(RunRecord run) {
        String base = "/api/runs/" + run.id();
        return new RunResponse(
                run.id(),
                run.type(),
                run.status(),
                run.processId(),
                run.createdAt(),
                run.startedAt(),
                run.completedAt(),
                run.cancelRequested(),
                run.errorCode(),
                run.errorMessage(),
                Map.of(
                        "self", base,
                        "result", base + "/result",
                        "cancel", base + "/cancel"));
    }
}
