import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from src.fetchers import fetch_all, deduplicate, filter_recent
from src.ai_filter import ai_filter_all
from src.ai_enricher import enrich_all, enrich_cfp_all
from src.ai_narrator import generate_narrative
from src.fallback_builder import build_fallback_report
from src.cfp_tracker import fetch_all_cfp_targets
from src.mailer import send_report, build_email
from src.sample_data import sample_items
from src.learning import LearningMemory, DEFAULT_MEMORY_FILE


def print_section(title):
    print(f"\n{'='*55}")
    print(f"  {title}")
    print(f"{'='*55}")


def collect_items(offline=False, max_items=None, memory=None):
    """Run steps 1-2 of the pipeline: fetch, deduplicate, recency filter."""
    if offline:
        print("  [OFFLINE] Using bundled sample data (no network access)")
        raw_items = sample_items()
        return raw_items

    raw_items = fetch_all()
    print(f"\n  Raw items collected: {len(raw_items)}")

    deduped = deduplicate(raw_items)
    print(f"  After deduplication: {len(deduped)}")

    recent = filter_recent(deduped, days=8)
    print(f"  After recency filter (8 days): {len(recent)}")

    if len(recent) == 0:
        print("  [WARN] No recent items found. Extending to 14 days...")
        recent = filter_recent(deduped, days=14)
        print(f"  After extended filter: {len(recent)}")

    if memory is not None:
        before = len(recent)
        unseen = memory.filter_unseen(recent)
        print(f"  After learning filter (previously seen dropped): "
              f"{before} → {len(unseen)}")
        recent = unseen

    if max_items:
        recent = recent[:max_items]
        print(f"  Capped to {max_items} items for this run")

    return recent


def analyze_items(recent, offline=False, personalization=None):
    """Run steps 3-6: AI filter, enrich, narrative (with fallback)."""
    # Split CFP RSS items from general items early
    general_items = [i for i in recent if i.get("category") != "cfp"]
    cfp_rss_items = [i for i in recent if i.get("category") == "cfp"]
    print(f"  General: {len(general_items)} | CFP from RSS: {len(cfp_rss_items)}")

    # ── STEP 2: CFP TARGET TRACKING ──────────────────────────
    print_section("STEP 2/8 — CFP Target Conference Tracking")
    if offline:
        print("  [OFFLINE] Skipping live CFP tracker (using sample CFP items)")
        cfp_target_items = []
    else:
        cfp_target_items = fetch_all_cfp_targets()

    # ── STEP 3: AI FILTER (general + cfp rss) ────────────────
    print_section("STEP 3/8 — AI Relevance Filtering (Groq)")
    filtered_general = ai_filter_all(general_items, personalization=personalization)
    filtered_cfp_rss = (
        ai_filter_all(cfp_rss_items, personalization=personalization)
        if cfp_rss_items else []
    )
    if not offline:
        time.sleep(2)

    # ── STEP 4: AI ENRICH — GENERAL ──────────────────────────
    print_section("STEP 4/8 — AI Enrichment: General Items (Groq)")
    enriched_general = enrich_all(filtered_general)
    if not offline:
        time.sleep(2)

    # ── STEP 5: AI ENRICH — CFP ──────────────────────────────
    print_section("STEP 5/8 — AI Enrichment: CFP Items (Groq)")
    all_cfp_items = cfp_target_items + filtered_cfp_rss
    enriched_cfp = enrich_cfp_all(all_cfp_items)
    if not offline:
        time.sleep(2)

    # Combine all items for narrative
    all_enriched = enriched_general + enriched_cfp

    # ── STEP 6: AI NARRATIVE ─────────────────────────────────
    print_section("STEP 6/8 — AI Report Narrative (Gemini 2.5 Flash)")
    narrative_html = generate_narrative(all_enriched, personalization=personalization)

    if narrative_html:
        print("  ✓ Gemini narrative generated successfully")
        report_body = narrative_html
    else:
        print("  ✗ Gemini failed — using structured fallback template")
        report_body = build_fallback_report(all_enriched)

    return all_enriched, report_body


def summarize(all_enriched, success, elapsed):
    high = sum(1 for i in all_enriched if i.get("priority") == "HIGH")
    med = sum(1 for i in all_enriched if i.get("priority") == "MEDIUM")
    low = sum(1 for i in all_enriched if i.get("priority") == "LOW")
    bd = sum(1 for i in all_enriched if i.get("bd_relevant"))
    cfp_count = sum(1 for i in all_enriched if i.get("category") == "cfp")
    print(f"\n  Priority breakdown: {high} HIGH | {med} MEDIUM | {low} LOW")
    print(f"  CFP items: {cfp_count} | BD-relevant: {bd}")

    print_section("STEP 8/8 — Pipeline Complete")
    print(f"""
  ┌─────────────────────────────────────┐
  │  ROBOWATCH WEEKLY RUN SUMMARY       │
  ├─────────────────────────────────────┤
  │  Report items        : {len(all_enriched):>4}          │
  │  CFP tracked items   : {cfp_count:>4}          │
  │  HIGH priority       : {high:>4}          │
  │  MEDIUM priority     : {med:>4}          │
  │  LOW priority        : {low:>4}          │
  │  BD-relevant items   : {bd:>4}          │
  │  Delivery            : {'✓ OK' if success else '✗ FAILED':>8}      │
  │  Total time          : {elapsed:>5}s         │
  └─────────────────────────────────────┘
""")
    return {
        "items": len(all_enriched),
        "cfp": cfp_count,
        "high": high,
        "medium": med,
        "low": low,
        "bd_relevant": bd,
        "delivered": bool(success),
        "elapsed_s": elapsed,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def write_report(report_body, stats, item_count, output_dir):
    """Write the dry-run artifacts (HTML report + stats JSON)."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    full_html = build_email(report_body, item_count=item_count)
    (out / "report.html").write_text(full_html, encoding="utf-8")
    (out / "report.json").write_text(
        json.dumps({"body": report_body, "stats": stats},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out / "stats.json").write_text(
        json.dumps(stats, indent=2), encoding="utf-8"
    )
    print(f"\n  📄 Dry-run artifacts written to: {out.absolute()}")
    return str(out)


def run(offline=False, dry_run=True, output_dir="output", max_items=None,
        memory_file=DEFAULT_MEMORY_FILE, feedback=None, learn=True):
    start_time = time.time()

    print("\n" + "🤖 " * 20)
    print("  ROBOWATCH AI — WEEKLY INTELLIGENCE PIPELINE")
    print("  " + datetime.now().strftime("%A, %B %d, %Y at %H:%M UTC"))
    print("🤖 " * 20)

    # ── STEP 0: LEARNING MEMORY ───────────────────────────────
    print_section("STEP 0/9 — Learning Memory")
    memory = LearningMemory(path=memory_file)
    feedback_applied = 0
    if feedback:
        pairs = memory.parse_feedback_spec(feedback)
        feedback_applied += len(memory.apply_feedback_pairs(pairs))
        print(f"  Applied {feedback_applied} inline feedback signal(s)")
    feedback_applied += len(memory.apply_feedback_file("feedback.txt"))
    if feedback_applied:
        print(f"  Total feedback applied this run: {feedback_applied}")

    personalization = memory.personalization_note()
    print(f"  Personalization: {personalization[:160]}")
    print(f"  Memory stats: {memory.stats()}")

    # ── STEP 1: COLLECT ──────────────────────────────────────
    print_section("STEP 1/9 — Data Collection")
    recent = collect_items(offline=offline, max_items=max_items,
                           memory=None if offline else memory)

    # ── STEPS 2-6: ANALYZE ───────────────────────────────────
    all_enriched, report_body = analyze_items(
        recent, offline=offline, personalization=personalization
    )

    # ── STEP 7: DELIVER ──────────────────────────────────────
    if dry_run:
        print_section("STEP 7/9 — Dry-Run (no email sent)")
        stats = summarize(all_enriched, True, round(time.time() - start_time, 1))
        stats["feedback_applied"] = feedback_applied
        stats["personalization"] = personalization
        result = write_report(report_body, stats, len(all_enriched), output_dir)
    else:
        print_section("STEP 7/9 — Multi-Email Delivery")
        success = send_report(report_body, item_count=len(all_enriched))
        stats = summarize(all_enriched, success, round(time.time() - start_time, 1))
        stats["feedback_applied"] = feedback_applied
        stats["personalization"] = personalization
        if os.environ.get("GITHUB_ACTIONS"):
            output_dir = os.environ.get("GITHUB_WORKSPACE", ".")
            write_report(report_body, stats, len(all_enriched), output_dir)
        result = success

    # ── STEP 8: LEARN ────────────────────────────────────────
    print_section("STEP 8/9 — Learning Update")
    if learn and not offline:
        memory.note_run(len(all_enriched))
        memory.save()
        print(f"  Memory saved to {memory.path} (seen={len(memory.data['seen'])}, "
              f"events={len(memory.data['events'])})")
    else:
        print("  [OFFLINE or --no-learn] Memory not persisted (read-only this run)")

    elapsed = round(time.time() - start_time, 1)
    print(f"\n  ✅ Total time: {elapsed}s")
    return result


def main():
    # Ensure emoji-heavy progress output does not crash on Windows consoles
    # that default to the cp1252 codec.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        prog="robowatch",
        description="RoboWatch — AI-powered weekly robotics intelligence digest.",
    )
    parser.add_argument(
        "--offline", action="store_true",
        help="Use bundled sample data instead of live RSS feeds (no network).",
    )
    parser.add_argument(
        "--dry-run", action="store_true", default=True,
        help="Write report.html + stats.json instead of sending email (default).",
    )
    parser.add_argument(
        "--send", action="store_true", dest="send",
        help="Actually deliver the report by email (requires SMTP secrets).",
    )
    parser.add_argument(
        "--output-dir", default="output",
        help="Directory for dry-run artifacts (default: output).",
    )
    parser.add_argument(
        "--max-items", type=int, default=None,
        help="Cap the number of items processed (useful for testing).",
    )
    parser.add_argument(
        "--memory-file", default=DEFAULT_MEMORY_FILE,
        help="Path to the learning-memory JSON file (default: memory/memory.json).",
    )
    parser.add_argument(
        "--feedback", default=None,
        help="Inline feedback, e.g. --feedback 'research:1,industry:-0.5' "
             "teaches category preferences.",
    )
    parser.add_argument(
        "--no-learn", action="store_true",
        help="Do not persist learning memory after this run.",
    )
    args = parser.parse_args()

    exit_code = run(
        offline=args.offline,
        dry_run=not args.send,
        output_dir=args.output_dir,
        max_items=args.max_items,
        memory_file=args.memory_file,
        feedback=args.feedback,
        learn=not args.no_learn,
    )
    raise SystemExit(0 if exit_code not in (False, None) else 1)


if __name__ == "__main__":
    main()
