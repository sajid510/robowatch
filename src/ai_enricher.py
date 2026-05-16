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