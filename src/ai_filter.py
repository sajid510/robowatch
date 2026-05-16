import os
import httpx
import json
import time

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

FILTER_SYSTEM = """You are a robotics intelligence filter for a Bangladeshi EEE undergraduate
student who leads a 3-person university robotics team building autonomous systems.

KEEP items about:
- Autonomous robotics, SLAM, ROS, path planning, perception, computer vision, LiDAR
- Robot hardware: actuators, sensors, embedded systems, microcontrollers, drones, arms
- AI in robotics: reinforcement learning, neural networks for navigation or manipulation
- Robotics competitions, hackathons, challenges open to international or undergraduate students
- Research breakthroughs in robotics (arXiv, IEEE, journals, conferences)
- Bangladesh robotics events: university competitions, local programs, BD tech news
- Fellowships, grants, calls for papers relevant to students in developing countries
- Open source robotics tools, frameworks, tutorials of engineering depth

DISCARD items about:
- Pure software AI with zero robotics application (ChatGPT updates, text models, image generators)
- Stock market, cryptocurrency, business acquisitions unrelated to robotics tech
- Opportunities exclusively for US/EU citizens with explicit visa or residency requirements
- Consumer gadgets and toys with no engineering value
- Vague press releases with no technical content
- Spam, clickbait, or content with no clear technical substance

IMPORTANT: Respond ONLY with a valid JSON array. Nothing else. No explanation. No markdown.
Each element must be exactly: {"index": <integer>, "keep": <true or false>, "reason": "<max 8 words>"}

Example of correct output:
[{"index": 0, "keep": true, "reason": "SLAM paper highly relevant"}, {"index": 1, "keep": false, "reason": "stock market news"}]"""


def call_groq(messages, max_tokens=600, temperature=0.1, retries=3):
    """Call Groq API with retry logic."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")

    for attempt in range(retries):
        try:
            response = httpx.post(
                GROQ_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
                timeout=40
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                wait = 10 * (attempt + 1)
                print(f"    [RATE LIMIT] Waiting {wait}s before retry...")
                time.sleep(wait)
            else:
                print(f"    [HTTP ERROR] {e.response.status_code}: {e}")
                break
        except Exception as e:
            print(f"    [ERROR] Attempt {attempt+1}: {e}")
            time.sleep(5)

    return None


def parse_json_response(raw_text):
    """Safely parse JSON from model response."""
    if not raw_text:
        return None
    # Strip markdown fences
    cleaned = raw_text.replace("```json", "").replace("```", "").strip()
    # Find JSON array
    start = cleaned.find("[")
    end = cleaned.rfind("]") + 1
    if start == -1 or end == 0:
        return None
    try:
        return json.loads(cleaned[start:end])
    except json.JSONDecodeError as e:
        print(f"    [JSON ERROR] {e}")
        return None


def ai_filter_batch(batch):
    """Filter a batch of up to 10 items using Groq."""
    numbered_items = "\n".join(
        f'{i}. [{item["category"].upper()}] TITLE: {item["title"]} | '
        f'SNIPPET: {item["raw_text"][:150]}'
        for i, item in enumerate(batch)
    )

    prompt = f"Filter these {len(batch)} robotics news items:\n\n{numbered_items}"

    raw = call_groq(
        messages=[
            {"role": "system", "content": FILTER_SYSTEM},
            {"role": "user", "content": prompt}
        ],
        max_tokens=600,
        temperature=0.1
    )

    decisions = parse_json_response(raw)

    if decisions is None:
        print("    [WARN] Could not parse filter response — keeping all items in batch")
        return {i: {"keep": True, "reason": "parse failed"} for i in range(len(batch))}

    return {d["index"]: d for d in decisions if "index" in d}


def ai_filter_all(items):
    """Run AI filtering on all items in batches of 10."""
    kept = []
    batch_size = 10
    total_batches = (len(items) + batch_size - 1) // batch_size

    for batch_num in range(total_batches):
        start = batch_num * batch_size
        batch = items[start:start + batch_size]

        print(f"    Batch {batch_num + 1}/{total_batches} "
              f"(items {start + 1}–{start + len(batch)})...")

        decisions = ai_filter_batch(batch)

        for local_idx, item in enumerate(batch):
            decision = decisions.get(local_idx, {"keep": True, "reason": "no decision"})
            if decision.get("keep", True):
                item["filter_reason"] = decision.get("reason", "")
                kept.append(item)
            else:
                print(f"      ✗ DISCARD: {item['title'][:55]} "
                      f"[{decision.get('reason', '')}]")

        # Rate limit protection between batches
        if batch_num < total_batches - 1:
            time.sleep(3)

    print(f"    Result: {len(items)} → {len(kept)} items kept")
    return kept
