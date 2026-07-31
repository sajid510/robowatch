# 07 — Configuration

All runtime configuration lives in version-controlled files plus environment
variables for secrets.

## Feeds — `config/sources.yaml`

```yaml
rss_feeds:
  industry:          # group name (used in logs)
    - url: "https://spectrum.ieee.org/feeds/topic/robotics.rss"
      category: "industry"     # drives report section placement
```

Seven groups ship by default: `industry`, `research`, `competitions`,
`conferences`, `fellowships`, `bangladesh`, `cfp`. Add or remove feeds freely —
each is capped at 12 entries per run.

## Target conferences — `src/cfp_tracker.py`

The `TARGET_CONFERENCES` list holds 12 curated venues (ICRA, IROS, ROBIO,
ROSCon, IEEE RAAICON, …). Each entry has `name`, `full_name`,
`search_query`, `known_venue`, `known_deadline`, `notes`, `relevance`, and
`bd_relevant`. Edit to track different venues.

## AI behaviour — module constants

| Constant | Location | Controls |
|---|---|---|
| `FILTER_SYSTEM` | `ai_filter.py` | Keep/discard rules for relevance filtering |
| `ENRICH_SYSTEM` | `ai_enricher.py` | JSON schema for enrichment |
| `CFP_ENRICH_SYSTEM` | `ai_enricher.py` | Venue-fit analysis prompt |
| `NARRATOR_SYSTEM` | `ai_narrator.py` | Report structure + writing voice |
| `GEMINI_MODEL` | `ai_narrator.py` | Default `gemini-2.5-flash-preview-05-20` |
| `GROQ_URL` | `ai_filter.py`, `ai_enricher.py` | Groq chat-completions endpoint |

## Subscribers — `subscribers.txt`

One email per line; `#` lines are ignored. Commit and push to apply changes.

## Secrets (environment variables)

| Variable | Used when | Fallback |
|---|---|---|
| `GROQ_API_KEY` | filtering + enrichment | keep-all + safe enrichment |
| `GEMINI_API_KEY` | narrative | structured fallback template |
| `GMAIL_ADDRESS` | delivery | report skipped (dry-run only) |
| `GMAIL_APP_PASSWORD` | delivery | report skipped (dry-run only) |
