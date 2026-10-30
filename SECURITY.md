# Security policy

## Supported deployment

Jase Vision AI is currently intended for local use and controlled, invite-only demonstrations. It is not yet a hardened public multi-user service.

## Reporting a vulnerability

Please do not publish credentials, access tokens, private network information or exploit details in a public issue. Use GitHub's private vulnerability reporting feature if it is enabled for this repository, or contact the repository maintainer privately through GitHub.

## Deployment safeguards

- Keep Flask bound to 127.0.0.1.
- Protect any remote hostname with Cloudflare Access or an equivalent authentication gateway.
- Do not expose Ollama's API port directly to the internet.
- Do not commit tunnel credentials, private keys, .env files, account tokens or local configuration.
- Apply request limits and keep the model host patched.
- Restrict demo access to trusted invitees.

## Known limitations

The current demo does not yet provide per-user quotas, rate limiting, malware scanning, a job queue or a concurrency scheduler. Do not treat it as production-ready for unrestricted public traffic.
