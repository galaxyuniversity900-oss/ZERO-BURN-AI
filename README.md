# ZERO-BURN AI
**Evidence-driven, cost-aware AI execution engine**

ZERO-BURN AI is a local-first foundation for reducing unnecessary model calls. It runs deterministic tasks locally, reuses only explicitly verified results, records each run, and refuses to pretend that an unconfigured model was called.

It is not a magical free replacement for frontier models. The goal is quality-adjusted cost reduction: spend inference only when local tools and proven procedures are insufficient.

## Current implementation
- Python 3.11+ core, SQLite evidence ledger, deterministic local task operations.
- Browser dashboard built with HTML/CSS/JavaScript.
- Local HTTP API with bounded request bodies and loopback-only default binding.
- Verified-only exact-task memory and usage statistics.
- Tests and GitHub Actions CI.
- PowerShell, shell, and Docker launch configurations.
- No provider integration is enabled in this foundation; no API key is needed.

## Run locally
```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate
pip install -e ".[dev]"
python -m zeroburn
```
Open http://127.0.0.1:8787.

PowerShell helper: `./scripts/run.ps1`. Linux/macOS helper: `sh scripts/run.sh`.

## Try local operations
Submit one of these in the dashboard:
- `UPPERCASE: evidence beats guesses`
- `LOWERCASE: ZERO-BURN AI`
- `COUNT WORDS: a local deterministic task`
- `SORT ALPHABETICALLY: pear, Apple, banana`

Other tasks return a clear “needs model or custom tool” result; they do not silently invoke a paid API.

## Verify
```bash
pip install -e ".[dev]"
pytest -q
python -m compileall -q src
```
CI runs the tests and compile check on pushes, pull requests, and manual dispatch.

## Architecture
```text
Browser → local HTTP API → task router
                         ├─ deterministic local operations
                         ├─ SQLite verified-solution ledger
                         ├─ run/budget telemetry
                         └─ (future opt-in) provider adapters
                                  ↓
                         independent verifier
```

## Configuration
- `ZERO_BURN_HOST`: defaults to `127.0.0.1`. Non-loopback binds are rejected by the server.
- `ZERO_BURN_PORT`: defaults to `8787`.
- `ZERO_BURN_DB`: defaults to `./data/zero_burn.sqlite3`.
- `ZERO_BURN_MAX_ATTEMPTS`: defaults to `3`, clamped to 1–10.
- `ZERO_BURN_BUDGET_UNITS`: defaults to `100`. These are internal planning units, not currency or token usage.

## Security notes
Do not expose this unauthenticated local dashboard to a LAN or public internet. Do not commit credentials. Generated code execution, provider APIs, MCP integrations, and automatic retries are not enabled in this foundation. Add authentication, authorization, rate limiting, CSRF protection, network controls, sandboxing, and real hard spending limits before a multi-user or internet-facing deployment.

## Project status
Foundation implementation, not production-certified software. CI results are authoritative for test status; a commit alone is not evidence that tests passed. See [docs/ROADMAP.md](docs/ROADMAP.md) and [docs/SECURITY.md](docs/SECURITY.md).
