# Architecture 04 — Module Dependency

## Import graph (runtime)

```
src/main
 ├── src/fetchers         (yaml, feedparser, re)
 ├── src/ai_filter        (httpx, json, time, os)
 ├── src/ai_enricher      (httpx, json, time, os)
 ├── src/ai_narrator      (httpx, json, os)
 ├── src/fallback_builder (—)
 ├── src/cfp_tracker      (feedparser, re)
 ├── src/mailer           (smtplib, email.mime)
 └── src/sample_data      (—)
```

## Rules

- **Acyclic** — dependencies flow one way: data modules → intelligence modules →
  presentation → orchestration. No cycles.
- **Isolated network layers** — `ai_filter`, `ai_enricher`, `ai_narrator`,
  `fetchers`, `cfp_tracker`, and `mailer` are the only modules that touch the
  network. `fallback_builder`, `sample_data`, and the test helpers are pure.
- **Testability** — `fallback_builder` and `sample_data` have no imports beyond
  stdlib, which is what lets the offline pipeline run with zero external
  dependencies at runtime (only `feedparser`/`httpx` are imported at module
  level by the network modules).

## Why no framework

The pipeline is a script run on a schedule — it needs no web framework,
database, or message broker. Keeping modules importable-and-callable means the
whole system can be tested and extended with plain functions.
