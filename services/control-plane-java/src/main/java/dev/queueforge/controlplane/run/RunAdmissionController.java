package dev.queueforge.controlplane.run;

import java.util.concurrent.Semaphore;
import java.util.concurrent.atomic.AtomicInteger;
import org.springframework.stereotype.Component;

@Component
public class RunAdmissionController {
    private final int maximum;
    private final Semaphore permits;
    private final AtomicInteger admitted = new AtomicInteger();

    public RunAdmissionController(WorkerSettings settings) {
        this.maximum = settings.maxOutstandingRuns();
        this.permits = new Semaphore(maximum, true);
    }

    public boolean tryAcquire() {
        if (!permits.tryAcquire()) {
            return false;
        }
        admitted.incrementAndGet();
        return true;
    }

    public void release() {
        while (true) {
            int current = admitted.get();
            if (current == 0) {
                return;
            }
            if (admitted.compareAndSet(current, current - 1)) {
                permits.release();
                return;
            }
        }
    }

    public Snapshot snapshot() {
        return new Snapshot(maximum, admitted.get(), permits.availablePermits());
    }

    public record Snapshot(int maximum, int admitted, int available) {
    }
}
