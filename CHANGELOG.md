# Changelog

All notable changes to RoboWatch are documented in this file.

---

## [1.2.0] - 2026-07-31

### Added

- **Self-learning memory** (`src/learning.py`) — the digest now learns every
  week: remembers seen articles (no repeats), tracks category preferences from
  feedback, and accumulates run stats.
- **Personalization** — learned category weights are injected into the Groq
  filter prompt and the Gemini narrator prompt, so the digest gets more
  customized with use.
- **Feedback channels** — `--feedback "cat:delta,…"` CLI flag and a committed
  `feedback.txt` file (lines like `research,1`) applied on every run.
- **Memory persistence** — `memory/memory.json` is committed back to the repo
  by the weekly GitHub Actions run (free, no database).
- Docs: `docs/16-self-learning.md`, updated README / config / workflow docs.
- Tests: 50+ tests including the learning module and pipeline integration.

---

## [1.1.0] - 2026-07-31

### Added

- CLI run modes: `--offline` (sample data, no network), `--dry-run`
  (artifacts, no email), `--send`, `--max-items`, `--output-dir`.
- Offline sample-data module (`src/sample_data.py`) for demos and tests.
- Dry-run artifacts: `report.html`, `report.json`, `stats.json`.
- Reusable `mailer.build_email()` and artifact upload in CI.
- Docker support (`Dockerfile`, `docker-compose.yml`, `.dockerignore`).
- CI test workflow (`.github/workflows/tests.yml`, Python 3.10–3.12).
- Expanded pytest suite (35+ tests) covering dedupe, mailer, fallback
  builder, and an offline end-to-end pipeline test.
- Full documentation: 15 docs, 8 architecture documents, README, architecture
  SVG, committed sample report in `examples/`.

### Changed

- `deduplicate()` now collapses near-duplicate titles (prefix matching ≥20
  chars) instead of exact-match only.
- `filter_recent()` keeps items without a usable publish date.
- AI filter keeps all items when `GROQ_API_KEY` is missing (was a hard error).
- Rate-limit sleeps are skipped when no API keys are configured.
- Emoji progress output no longer crashes on Windows cp1252 consoles
  (stdout is reconfigured to UTF-8).

---

## [1.0.0] - 2026-06-26

### Initial Release

- Robotics intelligence automation
- Weekly digest generation
- AI relevance filtering (Groq)
- AI enrichment (Groq)
- CFP target-conference tracking
- Gemini narrative + fallback template
- Email reporting (Gmail SMTP)
- Scheduled GitHub Actions workflow
