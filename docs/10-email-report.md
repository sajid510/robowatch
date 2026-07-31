# 10 — Email Report

## Layout

The email is assembled by `mailer.build_email` from:

1. **`EMAIL_CSS`** — dark theme (`#0a0a14` background), Inter font, priority
   colour coding (HIGH red, MEDIUM amber, LOW blue), CFP cards in purple.
2. **`EMAIL_WRAPPER`** — header band, content container, footer.
3. **The narrative body** — produced by Gemini (`ai_narrator`) or the fallback
   template (`fallback_builder`).

## Sections (Gemini narrative)

| # | Section | Content |
|---|---|---|
| 1 | 📋 Editor's Brief | Defining theme of the week + top action |
| 2 | ⭐ Top Pick This Week | Single most actionable item |
| 3 | 🏭 Industry & Breakthroughs | `industry` cards |
| 4 | 📄 Research Spotlight | `research` cards |
| 5 | 🏆 Competitions & Opportunities | `competition`/`conference`/`fellowship`, BD-flagged 🇧🇩 |
| 6 | 🇧🇩 Bangladesh Robotics Scene | `bangladesh` cards |
| 7 | 📝 Paper Submission Tracker | CFP cards with fit score + deadline table |
| 8 | ✅ Team Action Checklist | 4-6 concrete actions from HIGH items |
| 9 | 🔍 Quick Scan | LOW items as compact one-liners |

## Fallback template

When Gemini fails (or no key), `build_fallback_report` produces the same
section structure in pure Python: an editor brief, sectioned cards, a CFP
tracker table, an action checklist, and a quick-scan list. This guarantees a
useful report every week.

## Dry-run artifacts

`--dry-run` writes:

- `report.html` — full wrapped email, ready to open in a browser.
- `report.json` — `{body, stats}` of the raw narrative/fallback body.
- `stats.json` — counts, priority breakdown, delivery status, elapsed time.
