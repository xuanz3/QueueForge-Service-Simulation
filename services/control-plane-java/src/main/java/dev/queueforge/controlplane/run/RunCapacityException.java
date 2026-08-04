package dev.queueforge.controlplane.run;

public class RunCapacityException extends RuntimeException {
    private final RunAdmissionController.Snapshot capacity;

    public RunCapacityException(RunAdmissionController.Snapshot capacity) {
        super("Run capacity is full: "
                + capacity.admitted()
                + " of "
                + capacity.maximum()
                + " slots are occupied");
        this.capacity = capacity;
    }

    public RunAdmissionController.Snapshot capacity() {
        return capacity;
    }
}
