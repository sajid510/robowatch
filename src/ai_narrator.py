import os
import httpx
import json
from datetime import datetime

GEMINI_MODEL = "gemini-2.5-flash-preview-05-20"

NARRATOR_SYSTEM = """You are the editor of RoboWatch — a weekly robotics intelligence digest
written specifically for Niyari, a 3rd-year EEE student at University of Asia Pacific, Bangladesh,
leading a 3-person robotics team (Sadnan, Tazin, Akib) building autonomous systems on zero budget.

Your writing: precise, technical, direct, energizing. Like a senior engineer briefing a talented
junior. No filler words. No generic AI writing patterns. High signal only.

You will receive a JSON list of curated robotics items. Generate complete HTML for the email body.

STRUCTURE (use exactly these section headers as <h2> tags):

1. "📋 Editor's Brief" 
   A <div class="editor-brief"> containing 2-3 sentences. What was the defining theme this week?
   What is the single most important thing Niyari's team should act on?

2. "⭐ Top Pick This Week"
   A <div class="top-pick"> with the single most actionable item. Full paragraph: what it is,
   the technical details, why it matters for a BD student team, exact next step to take.

3. "🏭 Industry & Breakthroughs"
   Items with category 'industry'. Use card divs (see format below).

4. "📄 Research Spotlight"  
   Items with category 'research'. Emphasize what method/result is novel and how it applies
   to resource-constrained robot builds.

5. "🏆 Competitions & Opportunities"
   Items with category 'competition', 'conference', 'fellowship'.
   Sort by deadline (earliest first). Mark BD-eligible items with 🇧🇩.
   Show deadlines prominently in red if within 30 days.

6. "🇧🇩 Bangladesh Robotics Scene"
   Items with category 'bangladesh'. Write a 1-2 sentence connective intro before the cards.

7. "✅ Team Action Checklist"
   A <div class="checklist"><ul> with 4-6 specific, concrete action items for this week.
   Base these on HIGH priority items. Each item should name a specific action
   (e.g. "Register for X before May 30", "Read arXiv paper Y on SLAM", "Try ROS2 package Z").

8. "🔍 Quick Scan"
   LOW priority items as compact one-liner cards with just title link + source + date.
   No full card format needed here.

CARD HTML FORMAT (use for items in sections 3-6):
<div class="card PRIORITY">
  <div class="card-header">
    <span class="badge badge-PRIORITY">PRIORITY</span>
    <span class="score">Score: X/10</span>
  </div>
  <h3><a href="URL">TITLE</a></h3>
  <p class="summary">SUMMARY</p>
  <p class="reasoning"><em>Why this matters: REASONING</em></p>
  <div class="meta">
    📰 SOURCE | 📅 DATE
    [<span class="deadline">⏰ Deadline: DATE</span> if deadline exists]
    [🇧🇩 BD Eligible if bd_relevant is true]
    [🔧 KEY_TECH tags if key_tech array is not empty]
  </div>
</div>

Replace PRIORITY with exactly: HIGH, MEDIUM, or LOW (for CSS class matching).

Output ONLY the inner HTML body content. No <html>, <head>, <body>, or <style> tags.
The wrapper and CSS are handled externally."""


def build_payload(items):
    """Convert items list to compact JSON for Gemini."""
    payload = []
    for item in items:
        payload.append({
            "title": item["title"],
            "url": item["url"],
            "source": item["source"],
            "category": item["category"],
            "date": item["published_date"].strftime("%b %d, %Y"),
            "summary": item.get("summary", ""),
            "score": item.get("score", 5),
            "priority": item.get("priority", "MEDIUM"),
            "reasoning": item.get("reasoning", ""),
            "deadline": item.get("deadline"),
            "bd_relevant": item.get("bd_relevant", False),
            "key_tech": item.get("key_tech", []),
        })
    return json.dumps(payload, ensure_ascii=False)


def generate_narrative(items):
    """Use Gemini 2.5 Flash to write the full report narrative."""
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("    [WARN] GEMINI_API_KEY not set — skipping narrative generation")
        return None

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={api_key}"
    )

    week_str = datetime.now().strftime("%B %d, %Y")
    items_json = build_payload(items)
    item_count = len(items)

    prompt = (
        f"Today is {week_str}. Generate the RoboWatch weekly report.\n"
        f"Total items this week: {item_count}\n\n"
        f"Items data:\n{items_json}"
    )

    try:
        response = httpx.post(
            url,
            headers={"Content-Type": "application/json"},
            json={
                "system_instruction": {
                    "parts": [{"text": NARRATOR_SYSTEM}]
                },
                "contents": [
                    {"parts": [{"text": prompt}]}
                ],
                "generationConfig": {
                    "temperature": 0.4,
                    "maxOutputTokens": 8192,
                    "topP": 0.9,
                }
            },
            timeout=120  # Gemini can take longer for large outputs
        )
        response.raise_for_status()

        data = response.json()
        content = data["candidates"][0]["content"]["parts"][0]["text"]
        print(f"    Generated {len(content)} characters of HTML")
        return content

    except httpx.HTTPStatusError as e:
        print(f"    [HTTP ERROR] Gemini returned {e.response.status_code}")
        print(f"    Response: {e.response.text[:300]}")
        return None
    except Exception as e:
        print(f"    [ERROR] Gemini narrative failed: {e}")
        return None

def new_func():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    return api_key
