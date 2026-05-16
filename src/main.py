import time
from datetime import datetime

from src.fetchers import fetch_all, deduplicate, filter_recent
from src.ai_filter import ai_filter_all
from src.ai_enricher import enrich_all
from src.ai_narrator import generate_narrative
from src.fallback_builder import build_fallback_report
from src.mailer import send_report


def print_section(title):
    print(f"\n{'='*55}")
    print(f"  {title}")
    print(f"{'='*55}")


def run():
    start_time = time.time()

    print("\n" + "🤖 " * 20)
    print("  ROBOWATCH AI — WEEKLY INTELLIGENCE PIPELINE")
    print("  " + datetime.now().strftime("%A, %B %d, %Y at %H:%M UTC"))
    print("🤖 " * 20)

    # ── STEP 1: FETCH ────────────────────────────────────────
    print_section("STEP 1/6 — Data Collection")
    raw_items = fetch_all()
    print(f"\n  Raw items collected: {len(raw_items)}")

    # Basic deduplication before sending to AI
    deduped = deduplicate(raw_items)
    print(f"  After deduplication: {len(deduped)}")

    # Recency filter (last 8 days)
    recent = filter_recent(deduped, days=8)
    print(f"  After recency filter (8 days): {len(recent)}")

    if len(recent) == 0:
        print("  [WARN] No recent items found. Extending to 14 days...")
        recent = filter_recent(deduped, days=14)
        print(f"  After extended filter: {len(recent)}")

    # ── STEP 2: AI FILTER ────────────────────────────────────
    print_section("STEP 2/6 — AI Relevance Filtering (Groq)")
    filtered = ai_filter_all(recent)
    time.sleep(2)

    # ── STEP 3: AI ENRICH ────────────────────────────────────
    print_section("STEP 3/6 — AI Enrichment: Summary + Scoring (Groq)")
    enriched = enrich_all(filtered)
    time.sleep(2)

    # Stats
    high = sum(1 for i in enriched if i.get("priority") == "HIGH")
    med  = sum(1 for i in enriched if i.get("priority") == "MEDIUM")
    low  = sum(1 for i in enriched if i.get("priority") == "LOW")
    bd   = sum(1 for i in enriched if i.get("bd_relevant"))
    print(f"\n  Priority breakdown: {high} HIGH | {med} MEDIUM | {low} LOW")
    print(f"  Bangladesh-relevant: {bd} items")

    # ── STEP 4: AI NARRATIVE ─────────────────────────────────
    print_section("STEP 4/6 — AI Report Narrative (Gemini 2.5 Flash)")
    narrative_html = generate_narrative(enriched)

    if narrative_html:
        print("  ✓ Gemini narrative generated successfully")
        report_body = narrative_html
    else:
        print("  ✗ Gemini failed — using structured fallback template")
        report_body = build_fallback_report(enriched)

    # ── STEP 5: SEND ─────────────────────────────────────────
    print_section("STEP 5/6 — Multi-Email Delivery")
    success = send_report(report_body, item_count=len(enriched))

    # ── STEP 6: SUMMARY ──────────────────────────────────────
    elapsed = round(time.time() - start_time, 1)
    print_section("STEP 6/6 — Pipeline Complete")
    print(f"""
  ┌─────────────────────────────────────┐
  │  ROBOWATCH WEEKLY RUN SUMMARY       │
  ├─────────────────────────────────────┤
  │  Raw items fetched    : {len(raw_items):>4}          │
  │  After dedup + filter : {len(recent):>4}          │
  │  After AI filter      : {len(filtered):>4}          │
  │  Final report items   : {len(enriched):>4}          │
  │  HIGH priority        : {high:>4}          │
  │  MEDIUM priority      : {med:>4}          │
  │  LOW priority         : {low:>4}          │
  │  BD-relevant items    : {bd:>4}          │
  │  Email delivery       : {'✓ OK' if success else '✗ FAILED':>8}      │
  │  Total time           : {elapsed:>5}s         │
  └─────────────────────────────────────┘
""")


if __name__ == "__main__":
    run()
