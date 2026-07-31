# 16 — Self-Learning & Personalization

RoboWatch **learns from you every week** and uses what it learns to make the
next digest more customized — entirely on free infrastructure.

## The learning loop

```
        ┌───────────────────────────────────────────────┐
        │  1. LOAD memory/memory.json (last week's)     │
        │  2. Apply feedback (feedback.txt / --feedback)│
        │  3. Filter out articles you've already seen   │
        │  4. Build PERSONALIZATION note from weights   │
        │  5. Inject note into AI filter + narrator     │
        │  6. Save updated memory back to the repo      │
        └───────────────────────────────────────────────┘
```

## What the memory stores

| Memory | Learns from | Effect |
|---|---|---|
| `seen` URLs | Every delivered item | Never re-shows an article you've already seen |
| `weights` per category | Feedback events | Biases the AI filter + narrative toward/away from categories |
| `events` | Feedback rows | Auditable history of what you taught it |
| `stats` | Every run | `runs`, `items_shown`, `feedback_events` |

## How to teach it (3 ways)

### 1. Inline feedback (one-off)

```bash
python -m src.main --feedback "research:1,industry:-0.5,competition:0.75"
```

### 2. `feedback.txt` (persistent, recommended)

Add lines and commit — every run applies them:

```
research,1            # want MORE research
industry,-0.5         # want LESS industry
https://x.com/y,competition,1   # (optional) url, category, delta
```

### 3. Just let it run

Even without explicit feedback, the memory auto-tracks **seen items** so the
digest stays fresh, and each run's stats accumulate.

## Personalization injection

The learned weights are converted into a short note, e.g.:

> *"The reader values these categories most research (weight +1.0),
> competition (weight +0.75). Prioritize them. The reader de-prioritizes:
> industry (weight -0.5). Show less of these."*

This is appended to:

- **`FILTER_SYSTEM`** in `src/ai_filter.py` → keep/discard decisions follow
  your preferences.
- **`NARRATOR_SYSTEM`** in `src/ai_narrator.py` → emphasis and the weekly
  Top Pick reflect your interests.

## Persistence (free)

`memory/memory.json` is committed to the repository. The GitHub Actions
workflow adds a **"Persist learned memory"** step that commits the updated
memory back after every weekly run — so the learning survives between
serverless runs with no database and no cost.

## Inspecting the memory

```bash
python -c "from src.learning import LearningMemory; import json; print(json.dumps(LearningMemory().stats(), indent=2))"
```

Weights are clamped to `[-5, +5]`. `MAX_SEEN` caps the seen list at 4000 and
`MAX_EVENTS` at 500 to keep the file small.
