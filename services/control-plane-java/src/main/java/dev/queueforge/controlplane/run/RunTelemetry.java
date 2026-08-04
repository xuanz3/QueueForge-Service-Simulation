package dev.queueforge.controlplane.run;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import java.time.Duration;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import org.springframework.stereotype.Component;

@Component
public class RunTelemetry {
    private final AtomicInteger active = new AtomicInteger();
    private final Counter submitted;
    private final Counter rejected;
    private final Counter succeeded;
    private final Counter failed;
    private final Counter cancelled;
    private final Counter recovered;
    private final Timer duration;

    public RunTelemetry(MeterRegistry registry) {
        submitted = counter(registry, "queueforge.runs.submitted", "Accepted run requests");
        rejected = counter(registry, "queueforge.runs.rejected", "Rejected run requests");
        succeeded = counter(registry, "queueforge.runs.succeeded", "Successful runs");
        failed = counter(registry, "queueforge.runs.failed", "Failed runs");
        cancelled = counter(registry, "queueforge.runs.cancelled", "Cancelled runs");
        recovered = counter(registry, "queueforge.runs.recovered", "Runs failed during restart recovery");
        duration = Timer.builder("queueforge.runs.duration")
                .description("Worker run duration")
                .publishPercentileHistogram()
                .register(registry);
        Gauge.builder("queueforge.runs.active", active, AtomicInteger::get)
                .description("Runs currently executing")
                .register(registry);
    }

    public void submitted() {
        submitted.increment();
    }

    public void rejected() {
        rejected.increment();
    }

    public void started() {
        active.incrementAndGet();
    }

    public void completed(RunStatus status, long startedNanos) {
        active.updateAndGet(value -> Math.max(0, value - 1));
        terminal(status);
        duration.record(Duration.ofNanos(Math.max(0, System.nanoTime() - startedNanos)));
    }

    public void terminalWithoutStart(RunStatus status) {
        terminal(status);
    }

    public void recovered(int count) {
        if (count > 0) {
            recovered.increment(count);
        }
    }

    public Map<String, Object> snapshot() {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("active", active.get());
        result.put("submitted", submitted.count());
        result.put("rejected", rejected.count());
        result.put("succeeded", succeeded.count());
        result.put("failed", failed.count());
        result.put("cancelled", cancelled.count());
        result.put("recovered", recovered.count());
        result.put("meanDurationSeconds", duration.mean(java.util.concurrent.TimeUnit.SECONDS));
        return result;
    }

    private void terminal(RunStatus status) {
        switch (status) {
            case SUCCEEDED -> succeeded.increment();
            case FAILED -> failed.increment();
            case CANCELLED -> cancelled.increment();
            default -> {
            }
        }
    }

    private static Counter counter(MeterRegistry registry, String name, String description) {
        return Counter.builder(name).description(description).register(registry);
    }
}
