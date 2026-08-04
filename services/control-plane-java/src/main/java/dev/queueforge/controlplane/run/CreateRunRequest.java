package dev.queueforge.controlplane.run;

import jakarta.validation.constraints.NotNull;
import java.util.List;
import java.util.Map;

public record CreateRunRequest(
        @NotNull RunType type,
        @NotNull Map<String, Object> scenario,
        List<Integer> serverCounts,
        Integer runs,
        Long seedStart,
        Double targetP95Wait,
        Integer targetMaxQueue,
        Double targetMaxUtilisation,
        Double requiredSuccessRate) {
}
