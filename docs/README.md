# 📚 RoboWatch Documentation

RoboWatch is an AI-powered weekly robotics intelligence pipeline: it fetches
~40 RSS feeds, filters and enriches them with Groq, writes the weekly narrative
with Gemini, and emails a prioritized briefing to its subscribers.

## Getting started

| Doc | What it covers |
|---|---|
| [01 — Getting started](01-getting-started.md) | What RoboWatch is and what you need |
| [02 — Installation](02-installation.md) | Local + Docker install |
| [03 — Quick start](03-quick-start.md) | First dry-run in under a minute |
| [04 — Project structure](04-project-structure.md) | Repository layout |

## Deep dives

| Doc | What it covers |
|---|---|
| [05 — System architecture](05-system-architecture.md) | Modules and responsibilities |
| [06 — Data pipeline](06-data-pipeline.md) | The 8 pipeline steps |
| [07 — Configuration](07-configuration.md) | Feeds, prompts, subscribers |
| [08 — Workflows](08-workflows.md) | CFP tracking, run modes, scheduling |
| [09 — Deployment](09-deployment.md) | GitHub Actions + Docker + secrets |
| [10 — Email report](10-email-report.md) | Layout, styling, fallback template |
| [11 — AI pipeline](11-ai-pipeline.md) | Prompts, models, retries, fallbacks |
| [12 — API reference](12-api-reference.md) | Module function reference |
| [13 — FAQ](13-faq.md) | Common questions |
| [14 — Troubleshooting](14-troubleshooting.md) | Fixing common failures |
| [15 — Development guide](15-development-guide.md) | Contributing, testing, extending |
| [16 — Self-learning](16-self-learning.md) | Memory, feedback, personalization |

## Architecture documents

The `architecture/` folder holds the system-design view:

- [01 — System overview](../architecture/01-system-overview.md)
- [02 — Software architecture](../architecture/02-software-architecture.md)
- [03 — Data flow](../architecture/03-data-flow.md)
- [04 — Module dependency](../architecture/04-module-dependency.md)
- [05 — Deployment architecture](../architecture/05-deployment-architecture.md)
- [06 — Security](../architecture/06-security.md)
- [07 — Scalability](../architecture/07-scalability.md)
- [08 — Future architecture](../architecture/08-future-architecture.md)

The one-page visual is [`assets/architecture.svg`](../assets/architecture.svg).
