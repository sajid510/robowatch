# 09 — Deployment

## Option A — GitHub Actions (recommended)

The workflow `.github/workflows/weekly_report.yml` runs the full pipeline on a
Friday cron. Configure once:

1. Push the repository to GitHub.
2. Repository → Settings → Secrets and variables → Actions → New repository
   secret, and add:

   | Secret | Value |
   |---|---|
   | `GROQ_API_KEY` | Groq API key |
   | `GEMINI_API_KEY` | Google AI Studio API key |
   | `GMAIL_ADDRESS` | Gmail address that sends the report |
   | `GMAIL_APP_PASSWORD` | Gmail app password |

3. Run the workflow manually once (Actions → RoboWatch AI — Weekly Intelligence
   Report → Run workflow) to validate.
4. From then on it runs every Friday 08:00 UTC. The generated
   `report.html`/`stats.json` are attached as an artifact.

> Gmail app passwords require 2-Step Verification enabled on the account.
> See [Google's guide](https://support.google.com/accounts/answer/185833).

## Option B — Docker / self-hosted

```bash
docker compose up --build robowatch          # offline dry-run
docker compose run --rm --env-file .env robowatch --send
```

The entrypoint is `python -m src.main`; override `command` for the mode you
need.

## Option C — Local schedule (cron / Task Scheduler)

```bash
# Linux cron: every Friday 08:00 UTC
0 8 * * 5 cd /path/to/robowatch && .venv/bin/python -m src.main --send >> run.log 2>&1
```

On Windows use Task Scheduler with the same command.

## Verifying a run

- Check the run's **Summary** box: `Delivery : ✓ OK`.
- Inspect the uploaded artifact for the styled report.
- Confirm the receiving inbox shows the email with the RoboWatch theme.
