package dev.queueforge.controlplane.run;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

class RunStatusTest {
    @Test
    void identifiesTerminalStates() {
        assertFalse(RunStatus.QUEUED.isTerminal());
        assertFalse(RunStatus.RUNNING.isTerminal());
        assertTrue(RunStatus.SUCCEEDED.isTerminal());
        assertTrue(RunStatus.FAILED.isTerminal());
        assertTrue(RunStatus.CANCELLED.isTerminal());
    }
}
