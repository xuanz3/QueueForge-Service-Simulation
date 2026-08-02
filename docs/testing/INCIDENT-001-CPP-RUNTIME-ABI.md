# Incident 001: C++ Runtime ABI Mismatch

## Summary

The first complete Phase 1 verification built the QueueForge C++ executable
with GCC 14, then copied it into a Debian Bookworm runtime image. The executable
failed because the runtime `libstdc++.so.6` did not provide `GLIBCXX_3.4.32`.

## Impact

- The C++ image built successfully.
- The executable could not start in the final runtime image.
- The Phase 1 branch was not pushed and no Phase 1 pull request was created.

React, Java, Python and PostgreSQL verification had already passed.

## Root cause

The multi-stage image used different assumptions for the C++ build and runtime
environments. Dynamic linking allowed the build to succeed without proving that
the final image contained a compatible C++ standard library.

## Resolution

`queueforge-sim` now links the GCC C++ support libraries statically:

- `-static-libgcc`
- `-static-libstdc++`

The final Docker stage also executes:

```text
queueforge-sim --health
```

This turns runtime-loader compatibility into a build-time check.

## Prevention

- Repository verification requires the static runtime-link options.
- Repository verification requires a final-stage Docker health execution.
- The complete local verification still runs the short-lived worker after build.
- CI independently builds and tests the C++ project.

## Scope note

The executable remains dynamically linked to the system C library. The build
and runtime images continue to use compatible Debian Bookworm glibc.
