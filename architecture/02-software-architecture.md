# Architecture 02 — Software Architecture

## Module view

```
                    ┌────────────────────┐
                    │    src/main.py     │   CLI + orchestration
                    └───────┬────────────┘
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐  ┌─────────────────┐  ┌────────────────┐
│  fetchers.py  │  │  cfp_tracker.py │  │  ai_filter.py  │
└───────┬───────┘  └────────┬────────┘  └───────┬────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐  ┌─────────────────┐  ┌────────────────┐
│ ai_enricher.py│  │  ai_narrator.py │  │ fallback_build │
└───────┬───────┘  └────────┬────────┘  │     er.py      │
        │                   │           └───────┬────────┘
        ▼                   ▼                   │
┌───────────────┐  ┌─────────────────┐          │
│    mailer.py  │◄─┤  (report body)  │◄─────────┘
└───────┬───────┘  └─────────────────┘
        ▼
   subscribers
```

## Design principles

1. **Single responsibility** — each module owns exactly one pipeline concern.
2. **Data as plain dicts** — items flow as dictionaries; enrichment adds keys
   without restructuring.
3. **Graceful degradation** — every network/AI boundary has a fallback and is
   safe without keys.
4. **Configuration over code** — feeds in YAML, behaviour in prompt constants.
5. **Testable core** — pure functions (dedupe, scoring, rendering, JSON parsing)
   are unit-tested; the pipeline is integration-tested offline.

## Layers

- **Ingestion layer**: `fetchers.py`, `cfp_tracker.py`, `sample_data.py`.
- **Intelligence layer**: `ai_filter.py`, `ai_enricher.py`, `ai_narrator.py`.
- **Presentation layer**: `fallback_builder.py`, `mailer.py`.
- **Orchestration layer**: `main.py`.

## Dependency direction

`main` depends on all modules. `ai_enricher` is self-contained. `mailer`
depends on nothing internal. `sample_data` has no internal dependencies.

See [Architecture 04 — Module Dependency](04-module-dependency.md) for the
import graph.
