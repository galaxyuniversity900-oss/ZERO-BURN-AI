# Provider adapters

## Default behavior
No model is called unless `ZERO_BURN_PROVIDER` is explicitly configured. Deterministic local operations run before provider routing.

## Ollama (local inference)
1. Install and start Ollama on the same machine.
2. Pull a model supported by your hardware, for example a coding model.
3. Set `ZERO_BURN_PROVIDER=ollama` and optionally `OLLAMA_MODEL` / `OLLAMA_BASE_URL`.
4. Start ZERO-BURN AI and submit a task that is not handled by a deterministic operation.

The default endpoint is `http://127.0.0.1:11434`; the default model name is `qwen2.5-coder:7b`. Availability depends on what you have installed locally.

## OpenAI-compatible cloud endpoint
Set `ZERO_BURN_PROVIDER=openai-compatible`, `OPENAI_COMPATIBLE_BASE_URL`, `OPENAI_COMPATIBLE_MODEL`, and `OPENAI_COMPATIBLE_API_KEY`. This can incur charges. Keep credentials in environment variables or a secret manager; never commit them.

## Important limitations
- Provider responses are returned as unverified suggestions; the current foundation does not execute generated code.
- Usage counts are reported when the provider returns them, but this version does not calculate authoritative monetary costs or enforce a hard currency spend ceiling.
- `budget_units` are internal planning units, not dollars or tokens.
- Do not expose the server to untrusted networks. Add authentication, authorization, rate limiting, sandboxing, and hard provider billing controls before production use.
