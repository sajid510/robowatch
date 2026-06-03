import json
import os
import time
from datetime import datetime

import httpx

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

ENRICH_SYSTEM = """You are a robotics intelligence analyst.
Return ONLY valid JSON object with fields:
{
  "summary": "<=45 words",
  "score": <integer 1-10>,
  "priority": "HIGH|MEDIUM|LOW",
  "reasoning": "<=24 words",
  "bd_relevant": <true|false>,
  "deadline": "YYYY-MM-DD or null",
  "key_tech": ["up to 4 short tags"]
}
Use HIGH only for clearly actionable, time-sensitive, or major technical breakthroughs.
If no concrete deadline exists, set deadline to null.
"""


def _call_groq(messages, max_tokens=350, temperature=0.2, retries=3):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None

    for attempt in range(retries):
        try:
            response = httpx.post(
                GROQ_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
                timeout=45,
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
        except Exception:
            time.sleep(3 * (attempt + 1))

    return None


def _parse_json(text):
    if not text:
        return None
    cleaned = text.replace("```json", "").replace("```", "").strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}") + 1
    if start == -1 or end == 0:
        return None
    try:
        return json.loads(cleaned[start:end])
    except json.JSONDecodeError:
        return None


def _safe_enrichment(item):
    title = item.get("title", "")
    source = item.get("source", "")
    summary = item.get("raw_text", "")[:220]

    score = 6
    if item.get("category") in {"competition", "fellowship", "conference"}:
        score = 7
    if item.get("category") in {"research", "industry"}:
        score = 8

    priority = "MEDIUM" if score >= 7 else "LOW"

    return {
        "summary": summary or title,
        "score": score,
        "priority": priority,
        "reasoning": f"Useful {item.get('category', 'robotics')} update from {source}".strip(),
        "bd_relevant": item.get("category") == "bangladesh",
        "deadline": None,
        "key_tech": [],
    }


def _normalize_deadline(deadline_value):
    if not deadline_value:
        return None
    try:
        dt = datetime.fromisoformat(str(deadline_value).replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return None


def enrich_item(item):
    prompt = (
        f"Title: {item.get('title', '')}\n"
        f"Category: {item.get('category', '')}\n"
        f"Source: {item.get('source', '')}\n"
        f"Date: {item.get('published_date')}\n"
        f"URL: {item.get('url', '')}\n"
        f"Content: {item.get('raw_text', '')[:1200]}"
    )

    raw = _call_groq([
        {"role": "system", "content": ENRICH_SYSTEM},
        {"role": "user", "content": prompt},
    ])
    parsed = _parse_json(raw)

    enrich = parsed if isinstance(parsed, dict) else _safe_enrichment(item)

    item["summary"] = str(enrich.get("summary", _safe_enrichment(item)["summary"]))[:400]
    try:
        item["score"] = max(1, min(10, int(enrich.get("score", 6))))
    except Exception:
        item["score"] = 6

    p = str(enrich.get("priority", "MEDIUM")).upper()
    item["priority"] = p if p in {"HIGH", "MEDIUM", "LOW"} else "MEDIUM"
    item["reasoning"] = str(enrich.get("reasoning", ""))[:240]
    item["bd_relevant"] = bool(enrich.get("bd_relevant", item.get("category") == "bangladesh"))
    item["deadline"] = _normalize_deadline(enrich.get("deadline"))

    key_tech = enrich.get("key_tech", [])
    if isinstance(key_tech, list):
        item["key_tech"] = [str(k)[:30] for k in key_tech[:4]]
    else:
        item["key_tech"] = []

    return item


def enrich_all(items):
    enriched = []
    total = len(items)
    for idx, item in enumerate(items, start=1):
        print(f"    Enriching item {idx}/{total}...")
        enriched.append(enrich_item(item))
        if idx < total:
            time.sleep(1)

    enriched.sort(key=lambda i: (i.get("priority") != "HIGH", -(i.get("score") or 0)))
    print(f"    Enrichment complete: {len(enriched)} items processed")
    return enriched
  # ── CFP-SPECIFIC ENRICHMENT ───────────────────────────────────────────────────
# Appended below existing enrich_all — existing code is untouched.

CFP_ENRICH_SYSTEM = """You are a research publication advisor for Niyari, a final-year EEE
student in Bangladesh preparing their first conference paper on an autonomous indoor mobile robot.

The robot project (Team Supersonic) uses:
- Jetson Nano edge compute + Arduino Mega 2560 real-time controller
- RPLidar A1M8, Microsoft Kinect depth camera, MPU6050 IMU
- ROS 2 Humble, Nav2, SLAM Toolbox, Docker containers
- Zenoh middleware over Tailscale VPN (replacing DDS across network boundaries)
- Two-layer architecture: onboard edge layer + remote compute layer on laptop

Research angles: sensor fusion for low-cost platforms, edge-cloud compute partitioning,
GPS-denied indoor navigation, reliable pub/sub over VPN-tunnelled networks.

For the given conference/CFP item, return ONLY a valid JSON object with these fields:
{
  "summary": "2-3 sentences: what this venue is, its scope, and why it fits this specific project",
  "fit_score": <integer 1-10>,
  "fit_reasoning": "one sentence: which aspect of the project fits this venue",
  "submission_deadline": "extracted deadline or TBA",
  "conference_date": "when conference takes place or TBA",
  "venue_location": "City, Country or Online",
  "submission_type": "e.g. Full paper 8 pages IEEE / Extended abstract 2 pages / Talk proposal",
  "paper_fee": "fee info or Unknown — check official site",
  "action": "the single most important next step for the student right now"
}
No markdown. No text outside the JSON."""


def enrich_cfp_item(item):
    """CFP-specific AI enrichment using the project context prompt."""
    prompt = (
        f"Conference name: {item.get('cfp_name', item.get('title', ''))}\n"
        f"Full name: {item.get('title', '')}\n"
        f"Known venue: {item.get('cfp_venue', 'Unknown')}\n"
        f"Known deadline: {item.get('cfp_known_deadline', 'Unknown')}\n"
        f"Content: {item.get('raw_text', '')[:1000]}"
    )

    raw = _call_groq(
        messages=[
            {"role": "system", "content": CFP_ENRICH_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        max_tokens=500,
        temperature=0.15,
    )
    parsed = _parse_json(raw)

    if parsed and isinstance(parsed, dict):
        item["summary"] = str(parsed.get("summary", item.get("summary", "")))[:500]
        try:
            item["score"] = max(1, min(10, int(parsed.get("fit_score", item.get("score", 7)))))
        except Exception:
            pass
        item["priority"] = "HIGH" if item["score"] >= 8 else ("MEDIUM" if item["score"] >= 5 else "LOW")
        item["reasoning"] = str(parsed.get("fit_reasoning", item.get("reasoning", "")))[:240]
        item["deadline"] = parsed.get("submission_deadline") or item.get("deadline")
        item["cfp_conference_date"] = parsed.get("conference_date", "TBA")
        item["cfp_location"] = parsed.get("venue_location", item.get("cfp_venue", "TBD"))
        item["cfp_submission_type"] = parsed.get("submission_type", "Unknown")
        item["cfp_fee"] = parsed.get("paper_fee", "Unknown — check official site")
        item["cfp_action"] = parsed.get("action", "Monitor official site for CFP announcement")

    return item


def enrich_cfp_all(cfp_items):
    """Enrich all CFP target items with conference-specific AI analysis."""
    total = len(cfp_items)
    print(f"    Enriching {total} CFP items...")
    for idx, item in enumerate(cfp_items, start=1):
        print(f"    [{idx:02d}/{total}] {item.get('cfp_name', item['title'][:40])}...")
        enrich_cfp_item(item)
        if idx < total:
            time.sleep(1.5)
    return sorted(cfp_items, key=lambda x: x.get("score", 0), reverse=True)
