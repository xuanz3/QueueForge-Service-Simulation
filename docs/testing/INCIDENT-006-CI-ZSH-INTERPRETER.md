# Incident 006: Ubuntu CI Lacked the zsh Interpreter

## Summary

The complete Phase 4 lifecycle passed locally on macOS. The pull-request
workflow failed immediately when GitHub Actions attempted to execute the same
command.

## Observed failure

```text
./RUN_CONTROL_PLANE_DEMO.command: cannot execute: required file not found
Process completed with exit code 127
```

## Root cause

`RUN_CONTROL_PLANE_DEMO.command` intentionally uses zsh and declares:

```text
#!/bin/zsh
```

The file existed and retained executable mode. The Ubuntu runner did not have
`/bin/zsh`, so the kernel could not resolve the shebang interpreter.

## Resolution

The Java control-plane integration job installs zsh before executing the
lifecycle command.

## Prevention

Repository verification now requires the integration job to include:

- `sudo apt-get update`
- `sudo apt-get install -y zsh`
- the lifecycle command after the installation step

## Impact

No Java, PostgreSQL, C++ or Python test failed. The workflow stopped before
starting the lifecycle.
