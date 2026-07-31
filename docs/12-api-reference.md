# 12 — API Reference

## `src.fetchers`

| Function | Description |
|---|---|
| `load_sources()` | Loads and returns `config/sources.yaml` |
| `parse_date(entry)` | Extracts `published_parsed` → aware `datetime` (falls back to `updated_parsed`, then now) |
| `fetch_rss(url, category)` | Fetches one feed, returns normalized item dicts (max 12) |
| `fetch_all()` | Fetches all feeds from `sources.yaml` |
| `deduplicate(items)` | Removes duplicates by URL and near-duplicate titles |
| `filter_recent(items, days=8)` | Keeps items newer than `days` |

## `src.ai_filter`

| Function | Description |
|---|---|
| `call_groq(messages, max_tokens, temperature, retries)` | Chat-completions call with rate-limit backoff |
| `parse_json_response(raw_text)` | Strips fences/text, extracts and parses JSON array |
| `ai_filter_batch(batch)` | Filters ≤10 items via Groq |
| `ai_filter_all(items)` | Batches and runs the filter over all items |

## `src.ai_enricher`

| Function | Description |
|---|---|
| `_call_groq(messages, ...)` | Internal Groq call |
| `_safe_enrichment(item)` | Deterministic defaults when no key / parse fails |
| `enrich_item(item)` | Adds summary/score/priority/deadline/BD/tech-tags |
| `enrich_all(items)` | Enriches and sorts (HIGH → LOW, score desc) |
| `enrich_cfp_item(item)` | Venue-fit analysis for CFP items |
| `enrich_cfp_all(cfp_items)` | Enriches and sorts CFP items by fit score |

## `src.cfp_tracker`

| Function | Description |
|---|---|
| `fetch_all_cfp_targets()` | Returns structured items for all target conferences |

## `src.ai_narrator`

| Function | Description |
|---|---|
| `build_payload(items)` | Serializes items to compact JSON for Gemini |
| `generate_narrative(items)` | Returns HTML narrative string or `None` |

## `src.fallback_builder`

| Function | Description |
|---|---|
| `build_fallback_report(items)` | Deterministic HTML report from enriched items |

## `src.mailer`

| Function | Description |
|---|---|
| `load_subscribers()` | Parses `subscribers.txt` |
| `build_email(html_body, item_count)` | Wraps body with CSS/header/footer |
| `send_report(html_body, item_count)` | Delivers via Gmail SMTP; returns success bool |

## `src.main`

| Function | Description |
|---|---|
| `collect_items(offline, max_items)` | Steps 1-2 (fetch/dedupe/filter) |
| `analyze_items(recent, offline)` | Steps 3-6 (filter/enrich/narrate) |
| `write_report(report_body, stats, item_count, output_dir)` | Dry-run artifacts |
| `run(offline, dry_run, output_dir, max_items)` | Full pipeline entry point |
| `main()` | CLI parser (`--offline`, `--dry-run`, `--send`, `--max-items`, `--output-dir`) |
