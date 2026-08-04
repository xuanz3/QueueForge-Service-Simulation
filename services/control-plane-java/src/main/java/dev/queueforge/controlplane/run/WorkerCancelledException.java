package dev.queueforge.controlplane.run;

public class WorkerCancelledException extends RuntimeException {
    private static final long serialVersionUID = 1L;

    public WorkerCancelledException() {
        super("Worker execution was cancelled");
    }
}
