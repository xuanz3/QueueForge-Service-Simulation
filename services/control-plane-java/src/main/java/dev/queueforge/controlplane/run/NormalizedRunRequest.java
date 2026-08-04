package dev.queueforge.controlplane.run;

import java.util.List;
import java.util.Map;

public record NormalizedRunRequest(
        RunType type,
        Map<String, Object> scenario,
        List<Integer> serverCounts,
        int runs,
        long seedStart,
        double targetP95Wait,
        int targetMaxQueue,
        double targetMaxUtilisation,
        double requiredSuccessRate) {
}
