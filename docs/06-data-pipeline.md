# 06 — Data Pipeline

RoboWatch executes 8 steps in every run.

## Step 1 — Data collection (`fetchers.fetch_all`)

- Loads `config/sources.yaml` and fetches every feed via `feedparser`.
- Normalizes each entry into a dict:
  `{title, url, source, published_date, raw_text, category}`.
- Strips HTML from summaries and caps at 12 entries per feed.

## Step 2 — Deduplication + recency (`fetchers.deduplicate`, `filter_recent`)

- Dedupe by URL (ignoring query strings) and by **near-duplicate titles** —
  one title that is a prefix of another (≥20 chars) collapses into one.
- Keeps only items from the last 8 days; extends to 14 days if nothing survives.

## Step 3 — CFP target tracking (`cfp_tracker.fetch_all_cfp_targets`)

- For each of 12 curated target conferences, builds a structured item with
  venue, known deadline, relevance notes, and the latest Google News snippet.
- Skipped in `--offline` mode.

## Step 4 — AI filtering (`ai_filter.ai_filter_all`)

- Batches of 10 items → Groq decides `{index, keep, reason}`.
- Off-topic, spam, and low-value items are discarded. Missing key → keep all.

## Step 5 — AI enrichment (`ai_enricher.enrich_all`)

- Per item, Groq returns `{summary, score, priority, reasoning, bd_relevant,
  deadline, key_tech}`.
- CFP items go through `enrich_cfp_all` with a venue-fit prompt.

## Step 6 — Narrative (`ai_narrator.generate_narrative` / `fallback_builder`)

- Gemini 2.5 Flash writes the 9-section HTML narrative.
- On failure or missing key, `build_fallback_report` produces a deterministic
  structured report.

## Step 7 — Delivery (`mailer.send_report`)

- Wraps the body in CSS + header/footer, then SMTP/SSL to all subscribers.
- Dry-run instead writes `report.html`, `report.json`, `stats.json`.

## Step 8 — Summary

- Prints a boxed summary (items, priority breakdown, BD items, delivery status,
  elapsed time) and returns stats.

## Item schema (after enrichment)

```
{
  title, url, source, published_date, raw_text, category,
  summary, score (1-10), priority (HIGH/MEDIUM/LOW), reasoning,
  bd_relevant (bool), deadline (YYYY-MM-DD | null), key_tech [..],
  # CFP items additionally:
  cfp_name, cfp_venue, cfp_known_deadline, cfp_conference_date,
  cfp_location, cfp_submission_type, cfp_fee, cfp_action
}
```
