package dev.queueforge.controlplane.run;

import java.util.UUID;

public class RunNotFoundException extends RuntimeException {
    private static final long serialVersionUID = 1L;

    public RunNotFoundException(UUID id) {
        super("Run not found: " + id);
    }
}
