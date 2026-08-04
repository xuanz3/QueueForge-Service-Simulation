package dev.queueforge.controlplane.run;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

class ScenarioValidatorTest {
    private final ScenarioValidator validator = new ScenarioValidator();

    @Test
    void appliesAnalyticsDefaults() {
        NormalizedRunRequest result = validator.normalize(new CreateRunRequest(
                RunType.ANALYTICS,
                scenario(),
                null,
                null,
                null,
                null,
                null,
                null,
                null));

        assertEquals(List.of(3, 4, 5), result.serverCounts());
        assertEquals(40, result.runs());
        assertEquals(20260801L, result.seedStart());
    }

    @Test
    void rejectsInvalidTriangularOrder() {
        Map<String, Object> scenario = scenario();
        @SuppressWarnings("unchecked")
        Map<String, Object> service = (Map<String, Object>) scenario.get("service");
        service.put("minimumMinutes", 12);
        service.put("modeMinutes", 6);

        assertThrows(
                InvalidRunRequestException.class,
                () -> validator.normalize(new CreateRunRequest(
                        RunType.SIMULATION,
                        scenario,
                        null,
                        null,
                        null,
                        null,
                        null,
                        null,
                        null)));
    }

    static Map<String, Object> scenario() {
        Map<String, Object> scenario = new LinkedHashMap<>();
        scenario.put("schemaVersion", "1.0");
        scenario.put("simulation", new LinkedHashMap<>(Map.of(
                "durationMinutes", 480,
                "seed", 20260801)));
        scenario.put("arrivals", new LinkedHashMap<>(Map.of(
                "type", "poisson",
                "ratePerHour", 24)));
        scenario.put("service", new LinkedHashMap<>(Map.of(
                "type", "triangular",
                "minimumMinutes", 5,
                "modeMinutes", 8,
                "maximumMinutes", 14)));
        scenario.put("queue", new LinkedHashMap<>(Map.of(
                "discipline", "priority_fifo",
                "serverCount", 4,
                "priorityCustomerRatio", 0.15)));
        return scenario;
    }
}
