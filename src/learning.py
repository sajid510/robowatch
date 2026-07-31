"""Self-learning memory for RoboWatch.

RoboWatch gets better every week by persisting what it has learned into a
version-controlled ``memory/`` folder. Because memory is committed back to the
repo by GitHub Actions, the whole learning loop runs on **free infrastructure**
(no vector DB, no paid services).

What the memory learns from week to week:

- **Seen items** — URLs/titles already shown, so the digest never repeats an
  article the user already saw.
- **Category preferences** — a signed weight per category. Positive = the user
  values it (more coverage), negative = de-prioritize it. Weights are tuned by
  feedback events.
- **Feedback events** — explicit ratings recorded via ``--feedback``, the
  ``feedback.txt`` file, or future integrations. Each event is a small
  ``(item, category, delta, note)`` row the user can inspect.
- **Engagement stats** — counters that prove the system is learning (and that
  can be rendered in reports or READMEs).

The learned preferences are injected into the AI filter and narrator prompts,
which is what makes outputs *more customized and better over time*.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_MEMORY_FILE = "memory/memory.json"
MAX_SEEN = 4000
MAX_EVENTS = 500
DEFAULT_CATEGORIES = [
    "industry", "research", "competition", "conference",
    "fellowship", "bangladesh", "cfp",
]


def _now():
    return datetime.now(timezone.utc).isoformat()


class LearningMemory:
    """Persistent, JSON-backed memory for a RoboWatch deployment."""

    def __init__(self, path=DEFAULT_MEMORY_FILE, categories=None):
        self.path = Path(path)
        self.categories = categories or DEFAULT_CATEGORIES
        self.data = {
            "version": 1,
            "seen": {},
            "weights": {cat: 0.0 for cat in self.categories},
            "events": [],
            "stats": {"runs": 0, "items_shown": 0, "feedback_events": 0},
            "created_at": _now(),
            "updated_at": _now(),
        }
        self.load()

    # ── persistence ─────────────────────────────────────────────────────────
    def load(self):
        if self.path.exists():
            try:
                stored = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(stored, dict):
                    merged = self.data
                    merged.update({k: v for k, v in stored.items() if k in merged})
                    merged["weights"] = {
                        **{c: 0.0 for c in self.categories},
                        **{k: float(v) for k, v in (stored.get("weights") or {}).items()},
                    }
                    merged["seen"] = dict(stored.get("seen") or {})
                    merged["events"] = list(stored.get("events") or [])
                    self.data = merged
            except (json.JSONDecodeError, OSError) as exc:
                print(f"    [WARN] Could not load memory ({exc}) — starting fresh")
        return self

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data["updated_at"] = _now()
        self.path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return self

    # ── seen tracking ───────────────────────────────────────────────────────
    def _url_key(self, url):
        return str(url or "").split("?")[0].strip()

    def is_seen(self, item):
        return self._url_key(item.get("url", "")) in self.data["seen"]

    def record_seen(self, item):
        """Record an item as seen; returns True if it was new."""
        key = self._url_key(item.get("url", ""))
        if not key:
            return False
        if key in self.data["seen"]:
            return False
        self.data["seen"][key] = _now()
        self._prune_seen()
        return True

    def filter_unseen(self, items):
        """Return items not yet shown (and mark them seen)."""
        unseen = [i for i in items if not self.is_seen(i)]
        for item in unseen:
            self.record_seen(item)
        return unseen

    def _prune_seen(self):
        if len(self.data["seen"]) > MAX_SEEN:
            ordered = sorted(self.data["seen"].items(), key=lambda kv: kv[1])
            for key, _ in ordered[: len(ordered) - MAX_SEEN]:
                self.data["seen"].pop(key, None)

    # ── preferences / feedback ──────────────────────────────────────────────
    def _clamp_weight(self, value):
        return max(-5.0, min(5.0, round(float(value), 2)))

    def record_feedback(self, category, delta, url="", note=""):
        """Apply a signed preference delta for a category and log the event."""
        category = (category or "").strip().lower()
        if category not in self.data["weights"]:
            self.data["weights"][category] = 0.0
        self.data["weights"][category] = self._clamp_weight(
            self.data["weights"][category] + float(delta)
        )
        self.data["events"].append({
            "ts": _now(),
            "category": category,
            "delta": float(delta),
            "url": str(url or "")[:200],
            "note": str(note or "")[:200],
        })
        self.data["events"] = self.data["events"][-MAX_EVENTS:]
        self.data["stats"]["feedback_events"] = len(self.data["events"])
        return self.data["weights"][category]

    def apply_feedback_pairs(self, pairs):
        """Apply ``[(category, delta, url, note)]`` batches."""
        applied = []
        for pair in pairs:
            cat = str(pair[0] or "").strip().lower()
            delta = float(pair[1])
            url = pair[2] if len(pair) > 2 else ""
            note = pair[3] if len(pair) > 3 else ""
            if cat:
                self.record_feedback(cat, delta, url, note)
                applied.append((cat, delta))
        return applied

    def parse_feedback_spec(self, spec):
        """Parse ``--feedback`` values like ``research:1,industry:-0.5``."""
        pairs = []
        for chunk in re.split(r"[,;]", str(spec or "")):
            chunk = chunk.strip()
            if not chunk:
                continue
            parts = re.split(r":", chunk)
            if len(parts) == 2:
                try:
                    pairs.append((parts[0].strip(), float(parts[1].strip())))
                except ValueError:
                    print(f"    [WARN] Ignoring malformed feedback: {chunk}")
        return pairs

    def apply_feedback_file(self, path="feedback.txt"):
        """Read repo ``feedback.txt`` (lines: ``category,delta`` or
        ``url,category,delta``) and apply pending feedback."""
        f = Path(path)
        if not f.exists():
            return []
        applied = []
        for raw in f.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) == 2:
                try:
                    applied.extend(self.apply_feedback_pairs([(parts[0], parts[1])]))
                except ValueError:
                    continue
            elif len(parts) >= 3:
                try:
                    applied.extend(self.apply_feedback_pairs([(parts[1], parts[2], parts[0])]))
                except ValueError:
                    continue
        return applied

    # ── personalization context for prompts ────────────────────────────────
    def preferred_categories(self, top_n=3):
        """Categories with positive weight, best first."""
        ranked = sorted(
            self.data["weights"].items(), key=lambda kv: kv[1], reverse=True
        )
        return [(cat, w) for cat, w in ranked if w > 0][:top_n]

    def deprioritized_categories(self, top_n=3):
        ranked = sorted(self.data["weights"].items(), key=lambda kv: kv[1])
        return [(cat, w) for cat, w in ranked if w < 0][:top_n]

    def personalization_note(self):
        """A short prompt block describing learned preferences."""
        prefs = self.preferred_categories(4)
        deps = self.deprioritized_categories(3)
        events = self.data["stats"]["feedback_events"]

        lines = []
        if prefs:
            lines.append(
                "The reader values these categories most "
                + ", ".join(f"{cat} (weight {w:+.1f})" for cat, w in prefs)
                + ". Prioritize them."
            )
        if deps:
            lines.append(
                "The reader de-prioritizes: "
                + ", ".join(f"{cat} (weight {w:+.1f})" for cat, w in deps)
                + ". Show less of these."
            )
        if events:
            lines.append(f"The reader has given {events} feedback signals so far.")
        if not lines:
            lines.append("No learned preferences yet — default coverage.")
        return " ".join(lines)

    # ── stats ───────────────────────────────────────────────────────────────
    def stats(self):
        return {
            "seen_items": len(self.data["seen"]),
            "weights": dict(self.data["weights"]),
            "feedback_events": len(self.data["events"]),
            "runs": self.data["stats"]["runs"],
            "items_shown": self.data["stats"]["items_shown"],
        }

    def note_run(self, items_shown):
        self.data["stats"]["runs"] += 1
        self.data["stats"]["items_shown"] += int(items_shown or 0)
