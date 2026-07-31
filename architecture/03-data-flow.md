# Architecture 03 — Data Flow

## End-to-end flow

```
                ┌──────────────────────────────────────────────────────────┐
 config/        │                                                        │
 sources.yaml ──► FETCH (feedparser)          ┌──────────────┐            │
                │        │                    │ cfp_tracker  │            │
                │        ▼                    │ (12 venues)  │            │
                │   DEDUPE (url + title)      └──────┬───────┘            │
                │        ▼                           ▼                    │
                │   RECENCY (8 days)          structured CFP items        │
                │        │                           │                    │
                │        ▼                           ▼                    │
                │   AI FILTER (Groq)          AI FILTER (Groq)            │
                │        │                           │                    │
                │        ▼                           ▼                    │
                │   AI ENRICH (Groq)          AI ENRICH_CFP (Groq)        │
                │        │                           │                    │
                │        └──────────┬────────────────┘                    │
                │                   ▼                                     │
                │          AI NARRATE (Gemini)                            │
                │                   │                                     │
                │                   ▼                                     │
                │          FALLBACK TEMPLATE  ◄─── on failure / no key     │
                │                   │                                     │
                │                   ▼                                     │
                │            WRAP (CSS + header)                          │
                │                   │                                     │
                │                   ▼                                     │
                │      EMAIL (SMTP)   /    ARTIFACTS (--dry-run)          │
                └──────────────────────────────────────────────────────────┘
```

## Item lifecycle

1. **Raw** — `{title, url, source, published_date, raw_text, category}` from
   `fetch_rss` / `cfp_tracker`.
2. **Filtered** — adds `filter_reason` for kept items.
3. **Enriched** — adds `summary, score, priority, reasoning, bd_relevant,
   deadline, key_tech`; CFP items add `cfp_*` fields.
4. **Narrated** — serialized to compact JSON (`build_payload`) and handed to
   Gemini, or rendered directly by the fallback builder.
5. **Delivered** — embedded in the styled email wrapper.

## Artifacts

| Mode | Output |
|---|---|
| `--send` | Email to all subscribers |
| `--dry-run` | `report.html`, `report.json`, `stats.json` |
| CI (`--send` + `GITHUB_ACTIONS`) | Artifacts also uploaded to the run |

## Concurrency / ordering

The two data tracks (general + CFP) are processed independently and merged
only at enrichment; the final list is sorted HIGH → MEDIUM → LOW, then by score
descending. CFP items are additionally sorted by fit score descending within
their section.
