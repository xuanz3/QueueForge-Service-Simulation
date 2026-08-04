# Phase 8 Verification

Run:

```bash
./VERIFY_PHASE_8.command
```

## Final release contract

The command verifies:

- all Phase 0–7 repository, build, integration and performance gates
- all Phase 8 release files
- exactly eight tracked README PNG files
- exactly eight README image references in the required order
- valid screenshot dimensions and non-trivial file sizes
- release notes, summary and machine-readable manifest
- MIT license, changelog, security policy and contribution guide
- dedicated final-release GitHub Actions job
- healthy API, PostgreSQL and Web containers
- the normal interface on `http://localhost:15176`

## Evidence generation

Regenerate the portfolio evidence with:

```bash
./GENERATE_PORTFOLIO_EVIDENCE.command
```

The generator:

1. refreshes Phase 7 performance evidence
2. starts a temporary Web build on port `15177`
3. captures the real product through Dockerized Playwright
4. generates the README and release documentation
5. restores the normal stack on port `15176`

## Release

The Phase 8 start script merges the final pull request only after every
GitHub Actions check passes, then creates the annotated `v1.0.0` tag and
publishes the GitHub Release.
