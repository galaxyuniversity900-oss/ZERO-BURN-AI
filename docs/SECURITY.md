# Security model

- Default binding is loopback only.
- No provider is enabled in the foundation build.
- Never commit credentials, tokens, customer data, or local database files.
- Do not expose the local server to a LAN or public internet without authentication, authorization, CSRF protection, rate limiting, and TLS termination.
- Treat task prompts, tool output, files, and model responses as untrusted input.
- Never execute generated shell commands automatically without an isolated sandbox and explicit policy.
- Provider adapters must redact secrets from logs and enforce hard timeouts and cost ceilings.
- The Dockerfile binds inside the container to 0.0.0.0 for container reachability; publish ports only on localhost unless a hardened gateway is configured.
