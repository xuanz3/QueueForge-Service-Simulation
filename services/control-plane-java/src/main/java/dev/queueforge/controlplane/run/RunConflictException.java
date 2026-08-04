package dev.queueforge.controlplane.run;

public class RunConflictException extends RuntimeException {
    private static final long serialVersionUID = 1L;

    public RunConflictException(String message) {
        super(message);
    }
}
