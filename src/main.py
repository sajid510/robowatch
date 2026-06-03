import time
from datetime import datetime

from src.fetchers import fetch_all, deduplicate, filter_recent
from src.ai_filter import ai_filter_all
from src.ai_enricher import enrich_all, enrich_cfp_all
from src.ai_narrator import generate_narrative
from src.fallback_builder import build_fallback_report
from src.cfp_tracker import fetch_all_cfp_targets
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
    print_section("STEP 1/8 — Data Collection")
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

    # Split CFP RSS items from general items early
    general_items = [i for i in recent if i.get("category") != "cfp"]
    cfp_rss_items  = [i for i in recent if i.get("category") == "cfp"]
    print(f"  General: {len(general_items)} | CFP from RSS: {len(cfp_rss_items)}")

    # ── STEP 2: CFP TARGET TRACKING ──────────────────────────
    print_section("STEP 2/8 — CFP Target Conference Tracking")
    cfp_target_items = fetch_all_cfp_targets()

    # ── STEP 3: AI FILTER (general + cfp rss) ────────────────
    print_section("STEP 3/8 — AI Relevance Filtering (Groq)")
    filtered_general = ai_filter_all(general_items)
    if cfp_rss_items:
        filtered_cfp_rss = ai_filter_all(cfp_rss_items)
    else:
        filtered_cfp_rss = []
    time.sleep(2)

    # ── STEP 4: AI ENRICH — GENERAL ──────────────────────────
    print_section("STEP 4/8 — AI Enrichment: General Items (Groq)")
    enriched_general = enrich_all(filtered_general)
    time.sleep(2)

    # ── STEP 5: AI ENRICH — CFP ──────────────────────────────
    print_section("STEP 5/8 — AI Enrichment: CFP Items (Groq)")
    all_cfp_items = cfp_target_items + filtered_cfp_rss
    enriched_cfp = enrich_cfp_all(all_cfp_items)
    time.sleep(2)

    # Combine all items for narrative
    all_enriched = enriched_general + enriched_cfp

    # Stats
    high = sum(1 for i in all_enriched if i.get("priority") == "HIGH")
    med  = sum(1 for i in all_enriched if i.get("priority") == "MEDIUM")
    low  = sum(1 for i in all_enriched if i.get("priority") == "LOW")
    bd   = sum(1 for i in all_enriched if i.get("bd_relevant"))
    cfp_count = len(enriched_cfp)
    print(f"\n  Priority breakdown: {high} HIGH | {med} MEDIUM | {low} LOW")
    print(f"  CFP items: {cfp_count} | BD-relevant: {bd}")

    # ── STEP 6: AI NARRATIVE ─────────────────────────────────
    print_section("STEP 6/8 — AI Report Narrative (Gemini 2.5 Flash)")
    narrative_html = generate_narrative(all_enriched)

    if narrative_html:
        print("  ✓ Gemini narrative generated successfully")
        report_body = narrative_html
    else:
        print("  ✗ Gemini failed — using structured fallback template")
        report_body = build_fallback_report(all_enriched)

    # ── STEP 7: SEND ─────────────────────────────────────────
    print_section("STEP 7/8 — Multi-Email Delivery")
    success = send_report(report_body, item_count=len(all_enriched))

    # ── STEP 8: SUMMARY ──────────────────────────────────────
    elapsed = round(time.time() - start_time, 1)
    print_section("STEP 8/8 — Pipeline Complete")
    print(f"""
  ┌─────────────────────────────────────┐
  │  ROBOWATCH WEEKLY RUN SUMMARY       │
  ├─────────────────────────────────────┤
  │  Raw items fetched    : {len(raw_items):>4}          │
  │  After dedup + filter : {len(recent):>4}          │
  │  After AI filter      : {len(filtered_general):>4}          │
  │  General report items : {len(enriched_general):>4}          │
  │  CFP tracked items    : {cfp_count:>4}          │
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
