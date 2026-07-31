# Architecture 05 — Deployment Architecture

## Runtime topology

```
                    GitHub Actions (scheduled, Friday 08:00 UTC)
                    ┌───────────────────────────────────────────────┐
                    │  ubuntu-latest runner                         │
                    │  ┌─────────────┐                              │
                    │  │  Python 3.11 │                             │
                    │  │  RoboWatch   │◄── secrets: GROQ / GEMINI / │
                    │  │  pipeline    │     GMAIL_ADDRESS / PASSWORD│
                    │  └──────┬──────┘                              │
                    │         │                                      │
                    │  ┌──────▼──────┐   ┌─────────────────────────┐ │
                    │  │ upload-artifact ◄──│ report.html / stats.json │
                    │  └──────┬──────┘   └─────────────────────────┘ │
                    └─────────┼──────────────────────────────────────┘
                              │ SMTP/SSL 465
                              ▼
                         Gmail SMTP ──► subscribers' inboxes
```

## Alternative deployments

| Option | Notes |
|---|---|
| **Docker (self-hosted)** | `python:3.11-slim` image; `docker compose up --build`; cron/Task Scheduler invokes `--send` |
| **Local** | `python -m venv` + cron `0 8 * * 5` |
| **CI/CD** | `tests.yml` runs pytest on every push; `weekly_report.yml` schedules delivery |

## Configuration surface

- Secrets live in GitHub repository secrets (or `.env` for Docker).
- Feeds/subscribers are version-controlled — no runtime config service needed.

## Failure isolation

- AI stage failure → local fallback, delivery still attempted.
- SMTP failure → pipeline exits non-zero, artifact still written in CI.
- Feed failure → that feed is skipped; run continues.
