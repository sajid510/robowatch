# 02 — Installation

## Local installation

```bash
git clone https://github.com/sajid510/robowatch.git
cd robowatch

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Verify the install:

```bash
python -m pytest tests/ -q        # runs the full test suite
python -m src.main --offline      # offline smoke run → writes output/
```

## Docker installation

```bash
docker compose up --build robowatch
```

The image runs an offline dry-run by default so you can validate the build
without secrets. To deliver live:

```bash
docker compose run --rm --env-file .env robowatch --send
```

Create a `.env` file (git-ignored) with:

```
GROQ_API_KEY=...
GEMINI_API_KEY=...
GMAIL_ADDRESS=you@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
```

## GitHub Actions (scheduled)

No installation needed — the workflow in
`.github/workflows/weekly_report.yml` runs the pipeline on a cron. Add the
required [repository secrets](../README.md#github-actions-automatic) once, and
the report runs every Friday at 08:00 UTC.

## Requirements file

`requirements.txt` pins:

| Package | Purpose |
|---|---|
| `feedparser` | RSS/Atom parsing |
| `httpx` | HTTP client for Groq + Gemini APIs |
| `beautifulsoup4` | HTML text cleanup helpers |
| `jinja2` | Email templating utilities |
| `pyyaml` | Loading `config/sources.yaml` |
