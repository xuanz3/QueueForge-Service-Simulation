# Incident 009: Production Web Root Returned HTTP 404

## Summary

The Phase 5 React source compiled, the production bundle built and TypeScript
type checking passed. Runtime verification could connect to the published web
port, but the root document returned HTTP 404.

## Root cause and risk

The initial Phase 5 image built `dist` and then started Vite Preview in the
same build image. The existing Compose web container was not explicitly
removed before startup.

That arrangement left the verification result dependent on preview-server
behaviour and whether Compose replaced a previously created container.

## Resolution

The web service now uses a production multi-stage image:

1. Node 24 installs locked dependencies and builds Vite.
2. Nginx serves only the resulting `dist` directory.
3. Nginx listens on the existing container port 5173.
4. Unknown application routes fall back to `index.html`.
5. Static assets return 404 when genuinely missing.
6. The browser API address is supplied as a build argument.
7. The runtime demo removes the old web container and force-recreates services.

## Prevention

Phase 5 repository verification requires:

- the Node build stage
- the Nginx runtime stage
- the copied `dist` directory
- the Nginx foreground command
- port 5173 and SPA fallback configuration
- the Compose build argument
- removal and forced recreation of the web service

## Impact

No React workflow or backend service failed. The problem was isolated to how
the already-built frontend was served.
