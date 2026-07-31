# 13 — FAQ

**Do I need API keys to try it?**
No. `python -m src.main --offline --dry-run` needs no keys and no network.

**What if Groq or Gemini fails mid-run?**
The pipeline never crashes on AI failures. Filtering keeps all items, the
enricher uses safe defaults, and the narrative falls back to the structured
template.

**How much does a weekly run cost?**
Roughly one filter call per batch of 10, one enrichment call per item, and one
Gemini narrative call. At typical weekly volumes this is well within free-tier
limits for Groq and Google AI Studio.

**Can I add my own feeds?**
Yes — edit `config/sources.yaml`. Add feeds to an existing category or add a new
group with its own `category` value.

**How do I add/remove subscribers?**
Edit `subscribers.txt` (one email per line) and push. Lines starting with `#`
are ignored.

**How do I change what the AI keeps/discards?**
Edit `FILTER_SYSTEM` in `src/ai_filter.py`, or the report structure in
`NARRATOR_SYSTEM` in `src/ai_narrator.py`.

**Why are my CFP deadlines showing TBA?**
The tracker uses known deadlines from `TARGET_CONFERENCES` plus whatever Gemini
extracts from live Google News snippets. If a venue hasn't announced yet, it
stays TBA — monitor the official site (link is in the report).

**Where is my data stored?**
Nothing is stored server-side. The app runs in GitHub Actions on a schedule and
only sends email. No databases.

**How do I run it on a custom schedule?**
Change the `cron` in `.github/workflows/weekly_report.yml`, or run locally with
cron/Task Scheduler.

**Does it send to Gmail only?**
SMTP targets Gmail's server, but any account can be a *subscriber* — they just
receive the email at their address.
