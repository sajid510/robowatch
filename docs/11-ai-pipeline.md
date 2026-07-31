# 11 — AI Pipeline

RoboWatch uses two LLM providers for cost-efficient intelligence:

## Models

| Stage | Provider / Model | Token budget | Why |
|---|---|---|---|
| Filter | Groq `llama-3.3-70b-versatile` | 600 | Fast, cheap structured JSON decisions |
| Enrich | Groq `llama-3.3-70b-versatile` | 350 | Same, per-item |
| CFP enrich | Groq `llama-3.3-70b-versatile` | 500 | Venue-fit analysis |
| Narrative | Gemini `gemini-2.5-flash-preview-05-20` | 8192 | High-quality long-form HTML |

## Prompts

- **Filter** (`FILTER_SYSTEM`): lists what to keep (autonomous robotics, SLAM,
  ROS, competitions, BD events, fellowships, open-source tools) and what to
  discard (pure-software AI, spam, US/EU-only opportunities). Asks for a strict
  JSON array `{index, keep, reason}`.
- **Enrich** (`ENRICH_SYSTEM`): returns a strict JSON object with `summary`,
  `score`, `priority`, `reasoning`, `bd_relevant`, `deadline`, `key_tech`.
- **CFP** (`CFP_ENRICH_SYSTEM`): embeds the project's hardware stack (Jetson
  Nano, Arduino, RPLidar, Kinect, ROS 2, Nav2, Zenoh) so fit scores reflect the
  actual robot build.
- **Narrator** (`NARRATOR_SYSTEM`): defines the 9-section report structure,
  card HTML format, deadline urgency flags, and BD 🇧🇩 markers.

## Robustness

| Failure | Behaviour |
|---|---|
| Missing `GROQ_API_KEY` | filter keeps all items; enricher uses `_safe_enrichment` |
| Missing `GEMINI_API_KEY` | narrator returns `None` → fallback template |
| HTTP 429 (rate limit) | exponential backoff (`10s`, `20s`, `30s`) + batch sleeps |
| Malformed JSON | strict `_parse_json`; falls back to safe defaults |
| Gemini HTTP error | fallback to structured report, run still succeeds |

## Cost controls

- Filtering batches of 10 with `sleep(3)` between batches.
- 12-entry cap per feed; 8-day recency window.
- Single enrichment call per item with compact `raw_text[:1200]`.
