# 14 — Troubleshooting

## Pipeline runs but no email arrives

1. Confirm secrets are set: `GMAIL_ADDRESS`, `GMAIL_APP_PASSWORD`.
2. App passwords require **2-Step Verification** enabled on the Gmail account.
3. Check the run summary — `Email delivery: ✓ OK` means SMTP succeeded.
4. Check spam/Junk folders; the report is HTML.
5. Verify the address is in `subscribers.txt` (committed).

## `Gmail authentication failed`

- Regenerate the app password and update the secret.
- Ensure there are no spaces in the app password when pasted.
- Confirm the sender address matches the account that owns the app password.

## Groq/Gemini calls fail

- Verify keys are set as env vars / secrets.
- Check rate limits: the pipeline already backoff-retries 429s, but very large
  item counts may hit quotas. Use `--max-items` to cap.
- `GROQ_API_KEY not set` is printed when filtering is skipped — set the key to
  enable AI filtering/enrichment.

## No recent items found (`[WARN]`)

- The 8-day window may legitimately be empty (e.g., a quiet holiday week). The
  pipeline auto-extends to 14 days.
- Verify feeds in `sources.yaml` are reachable and publishing.

## Emoji output crashes on Windows (`UnicodeEncodeError`)

- This happens on consoles using the cp1252 codec. `python -m src.main` now
  reconfigures stdout to UTF-8 automatically. In older shells, set
  `$env:PYTHONIOENCODING="utf-8"` or use PowerShell 7+/Windows Terminal.

## Docker build fails

- Ensure Docker Desktop is running.
- The build runs an offline smoke test; it needs no secrets, but needs network
  to pull `python:3.11-slim` and pip packages on first build.

## Tests fail locally

- Install dev deps: `pip install -r requirements.txt pytest`.
- Tests are offline (no network, no keys). If they still fail, run
  `python -m pytest tests/ -q -x` and share the traceback.

## Debugging a report

Use `--dry-run --output-dir output` and open `output/report.html` in a browser,
or inspect `output/report.json` for the raw body + stats.
