# 03 — Quick Start

Get a working report in under a minute, no API keys required.

## 1. Offline demo (no keys, no email)

```bash
pip install -r requirements.txt
python -m src.main --offline --dry-run
```

The pipeline uses bundled sample data, skips all network calls, and writes:

- `output/report.html` — the full styled email (open in a browser).
- `output/report.json` — the fallback HTML body + stats.
- `output/stats.json` — item counts and priority breakdown.

## 2. Live AI run (dry, no email)

```bash
export GROQ_API_KEY=...
export GEMINI_API_KEY=...
python -m src.main --dry-run
```

Fetches real feeds, runs Groq filtering + enrichment, and lets Gemini write the
narrative — but only writes artifacts.

## 3. Deliver by email

```bash
export GMAIL_ADDRESS=you@gmail.com
export GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
python -m src.main --send
```

Sends the report to every address in `subscribers.txt`.

## 4. Schedule it

Push the `weekly_report.yml` workflow and add the four repository secrets. The
report runs every Friday 08:00 UTC automatically.
