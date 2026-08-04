package dev.queueforge.controlplane.run;

public class InvalidRunRequestException extends RuntimeException {
    private static final long serialVersionUID = 1L;

    public InvalidRunRequestException(String message) {
        super(message);
    }
}
