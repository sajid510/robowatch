# 05 — System Architecture

RoboWatch is a pipeline of small, single-purpose modules. Each stage consumes
the previous stage's output and produces a richer item or report.

![RoboWatch architecture](../assets/architecture.svg)

## Module responsibilities

| Module | Responsibility |
|---|---|
| `main.py` | Orchestrates the 8 pipeline steps; parses CLI flags |
| `fetchers.py` | Reads `config/sources.yaml`, fetches RSS, dedupes, filters by age |
| `ai_filter.py` | Batch-calls Groq to decide keep/discard per item |
| `ai_enricher.py` | Adds summary/score/priority/deadline/BD-flag/tech-tags; CFP variant |
| `cfp_tracker.py` | Curates 12 target conferences + latest Google News lookup |
| `ai_narrator.py` | Gemini writes the 9-section HTML narrative |
| `fallback_builder.py` | Pure-python fallback if the narrator fails or no key |
| `mailer.py` | Wraps the body with CSS and delivers over Gmail SMTP |
| `sample_data.py` | Offline items for `--offline` mode |

## Key design decisions

1. **Batching for cost control** — AI filtering runs in batches of 10 and the
   enricher processes one item at a time, with rate-limit sleeps between calls.
2. **Graceful degradation** — every AI stage has a deterministic fallback, so a
   missing key or failed API call never breaks delivery.
3. **Two-model split** — Groq (`llama-3.3-70b`) does cheap structured filtering
   and enrichment; Gemini (2.5 Flash) does the expensive creative narrative.
4. **CFP as a first-class track** — conference intelligence gets its own data
   source and prompt, scored against the project's actual research topics.
5. **Artifact-first delivery** — even real runs write `report.html`/`stats.json`
   so every weekly run is inspectable.
