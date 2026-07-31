# 08 — Workflows

## CFP / paper-submission tracking

The pipeline runs two parallel data tracks:

1. **RSS CFP track** — items tagged `category: cfp` from Google News feeds.
2. **Target-conference track** — `cfp_tracker.py` curates 12 venues and
   enriches each with a venue-fit score (1-10), submission deadline,
   conference dates, location, submission type, and fee.

Both tracks are enriched with `CFP_ENRICH_SYSTEM`, sorted by fit score, and
rendered in the **"Paper Submission Tracker"** report section with URGENT
flags for deadlines within 60 days.

## Run modes

| Mode | Command | Network | Email |
|---|---|---|---|
| Offline demo | `python -m src.main --offline` | none | no |
| Dry run | `python -m src.main --dry-run` | yes | no |
| Deliver | `python -m src.main --send` | yes | yes |

`--max-items N` caps items for quick tests; `--output-dir DIR` relocates
artifacts.

## Scheduled delivery

`.github/workflows/weekly_report.yml` triggers `0 8 * * 5` (Friday 08:00 UTC =
14:00 BST) with manual `workflow_dispatch` support. Generated artifacts are
uploaded via `actions/upload-artifact`.

## Adding a subscriber

Edit `subscribers.txt`, add the email, commit, and push. The next scheduled run
includes them. Remove the line to unsubscribe.
