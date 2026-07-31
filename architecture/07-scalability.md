# Architecture 07 — Scalability

## Current scale

- ~40 RSS feeds, capped at 12 entries each → ≤480 raw items per run.
- After dedupe + 8-day recency: typically 50–150 items.
- After AI filtering: typically 20–60 items to enrich.
- One email to a handful of subscribers, once a week.

## Bottlenecks and current mitigations

| Bottleneck | Current handling |
|---|---|
| LLM rate limits (429) | Batch filtering (10), backoff retries, sleeps between calls |
| Token cost | `raw_text[:1000-1200]` caps, compact prompts, 12-item feed cap |
| Run duration | `timeout-minutes: 25` in CI |
| Feed stalls | Per-feed try/except; a dead feed is skipped, not fatal |

## Scaling the reader base

1. **More subscribers** — the current loop is synchronous per recipient; for
   hundreds of recipients, batch via Gmail API (sendGrid-style) instead of SMTP
   one-by-one.
2. **More feeds** — the pipeline is O(items) in feeds; doubling feeds roughly
   doubles cost. Add a feed-quality weighting to de-prioritize low-signal feeds.
3. **Multiple digests** — the config is already generalized (see the
   sibling **NewsPulse** project, which parameterizes feeds/category/branding
   per publication).

## Scaling intelligence quality

- **Deduplication** uses exact+prefix matching; near-duplicate detection could
  be upgraded to embeddings for paraphrase-level dedupe.
- **Personalization** — add per-subscriber topic weights so scoring reflects
  each reader's focus areas.

## Operational scaling

- **Monitoring** — add a run-stats dashboard or GitHub Actions checks on
  `stats.json` (items, priority mix, delivery success).
- **Backfill** — add `--since` to rebuild reports for past weeks.

The architecture (function-per-stage) makes these extensions local changes
rather than rewrites.
