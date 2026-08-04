package dev.queueforge.controlplane.run;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Component;

@Component
public class ScenarioValidator {
    private static final List<Integer> DEFAULT_SERVER_COUNTS = List.of(3, 4, 5);

    public NormalizedRunRequest normalize(CreateRunRequest request) {
        if (request == null || request.type() == null || request.scenario() == null) {
            throw new InvalidRunRequestException("type and scenario are required");
        }

        Map<String, Object> scenario = deepMutableCopy(request.scenario());
        validateScenario(scenario);

        if (request.type() == RunType.SIMULATION) {
            return new NormalizedRunRequest(
                    RunType.SIMULATION,
                    scenario,
                    List.of(),
                    1,
                    readLong(mapAt(scenario, "simulation"), "seed"),
                    10.0,
                    20,
                    0.85,
                    0.90);
        }

        List<Integer> serverCounts = request.serverCounts() == null
                ? DEFAULT_SERVER_COUNTS
                : List.copyOf(request.serverCounts());
        int runs = request.runs() == null ? 40 : request.runs();
        long seedStart = request.seedStart() == null
                ? readLong(mapAt(scenario, "simulation"), "seed")
                : request.seedStart();
        double targetP95Wait = request.targetP95Wait() == null ? 10.0 : request.targetP95Wait();
        int targetMaxQueue = request.targetMaxQueue() == null ? 20 : request.targetMaxQueue();
        double targetMaxUtilisation = request.targetMaxUtilisation() == null
                ? 0.85
                : request.targetMaxUtilisation();
        double requiredSuccessRate = request.requiredSuccessRate() == null
                ? 0.90
                : request.requiredSuccessRate();

        validateAnalyticsSettings(
                serverCounts,
                runs,
                seedStart,
                targetP95Wait,
                targetMaxQueue,
                targetMaxUtilisation,
                requiredSuccessRate);

        return new NormalizedRunRequest(
                RunType.ANALYTICS,
                scenario,
                serverCounts,
                runs,
                seedStart,
                targetP95Wait,
                targetMaxQueue,
                targetMaxUtilisation,
                requiredSuccessRate);
    }

    void validateScenario(Map<String, Object> scenario) {
        if (!"1.0".equals(readString(scenario, "schemaVersion"))) {
            throw new InvalidRunRequestException("scenario.schemaVersion must be 1.0");
        }

        Map<String, Object> simulation = mapAt(scenario, "simulation");
        double duration = readDouble(simulation, "durationMinutes");
        long seed = readLong(simulation, "seed");
        if (duration <= 0 || duration > 1440) {
            throw new InvalidRunRequestException("simulation.durationMinutes must be in (0, 1440]");
        }
        if (seed < 0) {
            throw new InvalidRunRequestException("simulation.seed must be non-negative");
        }

        Map<String, Object> arrivals = mapAt(scenario, "arrivals");
        if (!"poisson".equals(readString(arrivals, "type"))) {
            throw new InvalidRunRequestException("arrivals.type must be poisson");
        }
        double rate = readDouble(arrivals, "ratePerHour");
        if (rate <= 0 || rate > 600) {
            throw new InvalidRunRequestException("arrivals.ratePerHour must be in (0, 600]");
        }

        Map<String, Object> service = mapAt(scenario, "service");
        if (!"triangular".equals(readString(service, "type"))) {
            throw new InvalidRunRequestException("service.type must be triangular");
        }
        double minimum = readDouble(service, "minimumMinutes");
        double mode = readDouble(service, "modeMinutes");
        double maximum = readDouble(service, "maximumMinutes");
        if (!(minimum > 0 && minimum <= mode && mode <= maximum && maximum <= 240)) {
            throw new InvalidRunRequestException(
                    "service minutes must satisfy 0 < minimum <= mode <= maximum <= 240");
        }

        Map<String, Object> queue = mapAt(scenario, "queue");
        String discipline = readString(queue, "discipline");
        if (!discipline.equals("fifo") && !discipline.equals("priority_fifo")) {
            throw new InvalidRunRequestException("queue.discipline must be fifo or priority_fifo");
        }
        int serverCount = readInt(queue, "serverCount");
        double priorityRatio = readDouble(queue, "priorityCustomerRatio");
        if (serverCount < 1 || serverCount > 100) {
            throw new InvalidRunRequestException("queue.serverCount must be between 1 and 100");
        }
        if (priorityRatio < 0 || priorityRatio > 1) {
            throw new InvalidRunRequestException("queue.priorityCustomerRatio must be between 0 and 1");
        }
    }

    private void validateAnalyticsSettings(
            List<Integer> serverCounts,
            int runs,
            long seedStart,
            double targetP95Wait,
            int targetMaxQueue,
            double targetMaxUtilisation,
            double requiredSuccessRate) {
        if (serverCounts.isEmpty() || serverCounts.size() > 10) {
            throw new InvalidRunRequestException("serverCounts must contain between 1 and 10 values");
        }
        if (serverCounts.stream().anyMatch(value -> value == null || value < 1 || value > 100)) {
            throw new InvalidRunRequestException("each server count must be between 1 and 100");
        }
        if (serverCounts.stream().distinct().count() != serverCounts.size()) {
            throw new InvalidRunRequestException("serverCounts must not contain duplicates");
        }
        if (runs < 2 || runs > 200) {
            throw new InvalidRunRequestException("runs must be between 2 and 200");
        }
        if (seedStart < 0) {
            throw new InvalidRunRequestException("seedStart must be non-negative");
        }
        if (targetP95Wait <= 0 || targetP95Wait > 240) {
            throw new InvalidRunRequestException("targetP95Wait must be in (0, 240]");
        }
        if (targetMaxQueue < 0 || targetMaxQueue > 100000) {
            throw new InvalidRunRequestException("targetMaxQueue must be between 0 and 100000");
        }
        if (targetMaxUtilisation <= 0 || targetMaxUtilisation > 1) {
            throw new InvalidRunRequestException("targetMaxUtilisation must be in (0, 1]");
        }
        if (requiredSuccessRate <= 0 || requiredSuccessRate > 1) {
            throw new InvalidRunRequestException("requiredSuccessRate must be in (0, 1]");
        }
    }

    @SuppressWarnings("unchecked")
    private static Map<String, Object> deepMutableCopy(Map<String, Object> source) {
        Map<String, Object> copy = new LinkedHashMap<>();
        source.forEach((key, value) -> {
            if (value instanceof Map<?, ?> map) {
                copy.put(key, deepMutableCopy((Map<String, Object>) map));
            } else if (value instanceof List<?> list) {
                copy.put(key, new ArrayList<>(list));
            } else {
                copy.put(key, value);
            }
        });
        return copy;
    }

    @SuppressWarnings("unchecked")
    private static Map<String, Object> mapAt(Map<String, Object> source, String key) {
        Object value = source.get(key);
        if (!(value instanceof Map<?, ?> map)) {
            throw new InvalidRunRequestException(key + " must be an object");
        }
        return (Map<String, Object>) map;
    }

    private static String readString(Map<String, Object> source, String key) {
        Object value = source.get(key);
        if (!(value instanceof String text) || text.isBlank()) {
            throw new InvalidRunRequestException(key + " must be a non-empty string");
        }
        return text;
    }

    private static double readDouble(Map<String, Object> source, String key) {
        Object value = source.get(key);
        if (!(value instanceof Number number)) {
            throw new InvalidRunRequestException(key + " must be numeric");
        }
        return number.doubleValue();
    }

    private static long readLong(Map<String, Object> source, String key) {
        Object value = source.get(key);
        if (!(value instanceof Number number)) {
            throw new InvalidRunRequestException(key + " must be numeric");
        }
        return number.longValue();
    }

    private static int readInt(Map<String, Object> source, String key) {
        long value = readLong(source, key);
        if (value < Integer.MIN_VALUE || value > Integer.MAX_VALUE) {
            throw new InvalidRunRequestException(key + " is outside the supported integer range");
        }
        return (int) value;
    }
}
