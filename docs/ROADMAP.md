# Roadmap

## Foundation (current)
- [x] Local-only HTTP service and dashboard
- [x] Standard-library task router
- [x] SQLite evidence ledger with verified-only reuse
- [x] Budget/run telemetry
- [x] Deterministic task examples and tests
- [x] CI workflow, Dockerfile, PowerShell and shell launchers

## Next stages
1. **Provider adapter protocol:** define structured input/output, cost reporting, timeout, retries, redaction, and opt-in provider activation.
2. **Model router:** benchmark-based capability table; task-specific routing; fallback and circuit breaker.
3. **Verification plugins:** unit tests, JSON schema validation, lint/build/test adapters, screenshot comparison.
4. **Sandbox:** isolated subprocess/container execution, resource caps, path allowlists, network disabled by default.
5. **Budget controls:** per-task and per-day currency limits, estimate vs actual usage, hard stop.
6. **Observability:** trace IDs, structured logs, exportable run history, privacy controls.
7. **Security:** authentication for non-loopback deployments, CSRF protections, rate limiting, dependency scanning.
8. **Multilingual UI:** Arabic RTL and English; localization tests.
9. **Evaluation harness:** fixed benchmark set, quality-adjusted cost, regression detection.
10. **Integrations:** optional MCP tool adapters and Blender automation after sandbox design.

## Acceptance criteria
- A model call is never made unless a provider is explicitly configured and enabled.
- Unknown or unverified solutions are never served as verified memory.
- Repeated identical failures terminate within the configured attempt limit.
- Every claimed saving is backed by measured baseline and actual usage.
- Tests pass on supported Python versions before release.
