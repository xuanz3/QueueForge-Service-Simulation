package dev.queueforge.controlplane.run;

import java.time.Instant;
import java.util.UUID;

public record RunRecord(
        UUID id,
        RunType type,
        RunStatus status,
        String requestJson,
        String resultJson,
        String errorCode,
        String errorMessage,
        Long processId,
        Instant createdAt,
        Instant startedAt,
        Instant completedAt,
        boolean cancelRequested) {
}
