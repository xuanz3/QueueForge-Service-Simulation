package dev.queueforge.controlplane.run;

public class WorkerExecutionException extends RuntimeException {
    private static final long serialVersionUID = 1L;

    private final String code;

    public WorkerExecutionException(String code, String message) {
        super(message);
        this.code = code;
    }

    public WorkerExecutionException(String code, String message, Throwable cause) {
        super(message, cause);
        this.code = code;
    }

    public String code() {
        return code;
    }
}
