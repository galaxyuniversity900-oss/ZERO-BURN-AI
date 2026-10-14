# ZERO-BURN AI
### Evidence-driven, cost-aware AI execution engine

ZERO-BURN AI is a local-first orchestration layer that reduces unnecessary model calls by routing deterministic work to tools, reusing only verified solutions, enforcing budgets, and escalating when evidence shows the current route is insufficient.

> It does not promise free frontier intelligence. It aims to minimize paid inference while preserving measurable task quality.

## Core principles
- **Tools before tokens:** deterministic checks, file operations, and tests run locally.
- **Evidence, not claims:** a solution is reusable only when its verification record passes.
- **Budget-aware routing:** local rules → optional low-cost model adapter → optional stronger adapter.
- **Bounded retries:** repeated failures without measurable progress stop automatically.
- **Provider-neutral:** provider integrations are adapters; no API key is required for local mode.
- **Privacy-first defaults:** local HTTP server binds to 127.0.0.1; never expose it publicly without authentication.

## Quick start
Requires Python 3.11+.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
python -m zeroburn
```

Open http://127.0.0.1:8787

No cloud credentials are needed for the dashboard, budget engine, local rules, or evidence ledger. Model adapters are intentionally opt-in.

## Verify
```bash
pip install -e ".[dev]"
pytest
python -m compileall src
```

## Architecture
```text
Browser UI → Local API → Task Planner
                        ├─ deterministic tools
                        ├─ verified solution ledger (SQLite)
                        ├─ budget / retry guard
                        └─ model adapter interface (optional)
                              ↓
                      evidence-based verifier
                              ↓
                       result + audit record
```

## Configuration
Environment variables:
- `ZERO_BURN_HOST` (default `127.0.0.1`)
- `ZERO_BURN_PORT` (default `8787`)
- `ZERO_BURN_DB` (default `./data/zero_burn.sqlite3`)
- `ZERO_BURN_MAX_ATTEMPTS` (default `3`)
- `ZERO_BURN_BUDGET_UNITS` (default `100`; internal planning units, not currency)

Do not put secrets in the repository. Future provider adapters should read credentials from environment variables or a secret manager and must never log them.

## Status
This is an initial, testable foundation—not a claim of production certification. The included local route is functional; real provider integrations, sandboxed code execution, authentication, and deployment hardening should be added before exposing it to untrusted users.
