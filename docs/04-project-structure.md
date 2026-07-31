# 04 — Project Structure

```
robowatch/
├── src/                       # Python package
│   ├── main.py                # CLI + pipeline orchestration (steps 1-8)
│   ├── fetchers.py            # RSS fetch, dedupe (URL + title), recency
│   ├── ai_filter.py           # Groq relevance filter (batch of 10)
│   ├── ai_enricher.py         # Groq enrichment + CFP-specific enrichment
│   ├── ai_narrator.py         # Gemini 2.5 Flash report narrative
│   ├── fallback_builder.py    # Deterministic fallback HTML report
│   ├── cfp_tracker.py         # Target-conference tracking + Google News lookup
│   ├── mailer.py              # Email assembly + Gmail SMTP delivery
│   ├── sample_data.py         # Offline sample items for --offline
│   └── __init__.py
├── config/
│   └── sources.yaml           # RSS feed definitions by category
├── examples/                  # Generated sample report (committed)
├── docs/                      # 15 user-facing docs + index
├── architecture/              # 8 system-design documents
├── assets/
│   └── architecture.svg       # Pipeline diagram
├── tests/                     # pytest suite (fetchers, filter, mailer,
│                              #   fallback, pipeline E2E)
├── .github/workflows/
│   ├── weekly_report.yml      # Friday cron delivery
│   └── tests.yml              # CI on push/PR (Python 3.10-3.12)
├── Dockerfile                 # Multi-stage container image
├── docker-compose.yml         # Compose service (offline dry-run default)
├── requirements.txt
├── subscribers.txt            # Email list (one per line)
├── SECURITY.md  CONTRIBUTING.md  CHANGELOG.md  ROADMAP.md  CITATION.cff
└── LICENSE
```
