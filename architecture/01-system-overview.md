# Architecture 01 — System Overview

![RoboWatch architecture](../assets/architecture.svg)

## Objectives

RoboWatch turns noisy robotics RSS feeds into a high-signal, prioritized weekly
briefing. The goals are:

1. **Signal over noise** — AI filtering and enrichment reduce ~hundreds of raw
   items to a curated digest the reader can act on.
2. **Opportunity capture** — competitions, fellowships, and CFPs are tracked
   with deadlines and fit scoring, so time-sensitive items are never missed.
3. **Zero-ops automation** — a scheduled GitHub Actions cron runs everything
   without a server.
4. **Resilience** — every AI stage has a deterministic fallback; the pipeline
   never breaks because an LLM is unavailable.

## High-Level Architecture

RoboWatch is a linear pipeline of single-purpose Python modules orchestrated by
`src/main.py`:

```
sources.yaml ─► fetch ─► dedupe ─► AI filter ─► enrich ─► narrate ─► deliver
cfp_tracker ─►  (target conferences) ─► enrich_cfp ─┘
```

## Component Overview

| Component | Role |
|---|---|
| `fetchers` | Ingest + normalize RSS items |
| `cfp_tracker` | Curated conference intelligence |
| `ai_filter` | Keep/discard decisions via Groq |
| `ai_enricher` | Scores, summaries, deadlines, tags |
| `ai_narrator` | Gemini-written HTML narrative |
| `fallback_builder` | Deterministic report when narrator fails |
| `mailer` | HTML email assembly + SMTP delivery |
| `main` | Orchestration + CLI |

## Processing Pipeline

Detailed in [Architecture 03 — Data Flow](03-data-flow.md) and
[`docs/06-data-pipeline.md`](../docs/06-data-pipeline.md). In brief: fetch →
dedupe → recency filter → (CFP track parallel) → AI filter → AI enrich → AI
narrate (or fallback) → deliver or dry-run artifacts.

## External Services

| Service | Use |
|---|---|
| RSS feeds | ~40 sources in `config/sources.yaml` |
| Groq API | `llama-3.3-70b` filtering + enrichment |
| Gemini API | `gemini-2.5-flash` narrative |
| Gmail SMTP | Report delivery |
| GitHub Actions | Scheduled execution + secrets |

## Output Generation

A single styled HTML email with nine sections (Editor's Brief, Top Pick,
Industry, Research, Opportunities, Bangladesh, Paper Tracker, Action
Checklist, Quick Scan). Dry-run mode writes `report.html`, `report.json`, and
`stats.json`.
