# Phase 5 Verification

Run:

```bash
./VERIFY_PHASE_5.command
```

The gate verifies:

- all previous repository contracts
- the typed React control-plane client
- scenario and analytics validation
- responsive product-interface source markers
- TypeScript type checking and production build
- Docker Compose configuration
- deployed HTML and JavaScript bundle availability
- real API readiness
- a real simulation submitted through the deployed local stack
- persisted successful result retrieval

Runtime evidence is written to `runtime/phase5/ui-runtime-evidence.json`.

The browser bundle is checked for the committed workflow strings so a stale
foundation page cannot pass merely because Vite is serving an index document.
