# Incident 010: Type Checking Was Invoked in the Nginx Image

## Summary

The React production build and Nginx root document passed. The complete Phase
5 verification gate then attempted to run npm in the final web service.

## Observed failure

```text
/docker-entrypoint.sh: exec: line 47: npm: not found
```

## Root cause

`VERIFY_PHASE_5.command` still used:

```text
docker compose run --rm -T --no-deps web npm run typecheck
```

The Compose web service now correctly resolves to a minimal Nginx image.

## Resolution

The Dockerfile exposes a dedicated Node stage:

```dockerfile
FROM build AS typecheck
RUN npm run typecheck
```

The verification gate builds that target explicitly. The Nginx image remains
free of build tooling.

## Prevention

Repository verification requires the typecheck stage and rejects npm execution
through the final Compose web service.

## Impact

No React, Nginx or backend functionality failed.
