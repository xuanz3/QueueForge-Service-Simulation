package dev.queueforge.controlplane.run;

import java.nio.file.Path;
import java.util.List;

record WorkerPlan(
        List<String> command,
        Path resultPath,
        Path stdoutPath,
        Path stderrPath) {
}
