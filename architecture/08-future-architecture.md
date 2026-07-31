# Architecture 08 — Future Architecture

## Vision

RoboWatch becomes a **personal robotics intelligence platform**: one scheduled
ingestion, many tailored digests, and a feedback loop that improves scoring
from reader behaviour.

## Proposed evolution

```
                ┌───────────────────────────────────────────────────┐
                │            ROBOWATCH PLATFORM (future)            │
                │                                                   │
 Sources ─► ingestion ─► embeddings / dedupe ─► AI filter           │
 (RSS,arXiv,                                             │          │
  GitHub,events)                                          ▼         │
                 ┌───────────► scoring + personalization ◄──────────┐
                 │             (reader feedback loop)              │
                 ▼                                                  │
   digest configs ─► render (HTML / MD / JSON) ◄────────────────────┘
                 │
                 ▼
   delivery: email · GitHub Pages · RSS-out · webhooks
```

## Roadmap phases

| Phase | Work |
|---|---|
| **1. Quality** | Embedding-based near-dup dedupe; topic embeddings for scoring; feed-quality weights |
| **2. Personalization** | Per-subscriber topic weights + `--since` backfill; per-reader digests |
| **3. Distribution** | Render digest to GitHub Pages (HTML site) and RSS-out; webhook delivery |
| **4. Platform** | Multi-digest configs (already proven by NewsPulse); a web dashboard for subscribers |
| **5. Observability** | Stats endpoint, run dashboards, alerting on delivery failure |

## Design guardrails

Keep the current invariants:

1. **No persistence by default** — artifacts are files, not a database.
2. **Deterministic fallbacks** for every AI step.
3. **Config-driven** feeds/prompts/digests.
4. **Pure core** modules stay unit-testable offline.

This keeps growth additive: each phase is new modules + config, not a rewrite.
