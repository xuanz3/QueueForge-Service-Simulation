# Phase 8 Verification

Run:

```bash
./VERIFY_PHASE_8.command
```

## Release contract

The command verifies:

- all Phase 0–7 repository, build, integration and performance checks
- all Phase 8 release files
- exactly eight tracked README PNG screenshots
- exactly eight README image references in the required order
- valid screenshot dimensions and non-trivial file sizes
- release notes, project summary and machine-readable manifest
- MIT license, changelog, security policy and contribution guide
- the dedicated release-verification GitHub Actions job
- healthy API, PostgreSQL and Web containers
- the normal interface on `http://localhost:15176`

## Screenshot capture

Regenerate the screenshots and release documents with:

```bash
./scripts/release/CAPTURE_PRODUCT_SCREENSHOTS.command
```

The command:

1. refreshes the reliability and performance checks
2. starts a temporary Web build on port `15177`
3. captures the running product through Dockerized Playwright
4. updates the README and release documents
5. restores the normal stack on port `15176`

## Release

The `v1.0.0` tag remains immutable. Later documentation and presentation
maintenance is delivered through normal pull requests on `main`.
