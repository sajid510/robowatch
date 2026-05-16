import feedparser
import httpx
from datetime import datetime, timezone, timedelta
import yaml
from pathlib import Path


def load_sources():
    with open("config/sources.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_date(entry):
    """Extract publication date from feed entry."""
    for field in ["published_parsed", "updated_parsed"]:
        t = getattr(entry, field, None)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    return datetime.now(timezone.utc)


def fetch_rss(url, category):
    """Fetch a single RSS feed and return normalized items."""
    items = []
    try:
        # feedparser handles the HTTP request itself
        feed = feedparser.parse(url)

        if not feed.entries:
            print(f"    [SKIP] No entries from: {url[:60]}")
            return items

        for entry in feed.entries[:12]:  # cap 12 per feed
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            summary = entry.get("summary", "") or entry.get("description", "")

            # Skip if no title or link
            if not title or not link:
                continue

            # Clean HTML from summary
            import re
            summary = re.sub(r"<[^>]+>", " ", summary)
            summary = re.sub(r"\s+", " ", summary).strip()

            items.append({
                "title": title,
                "url": link,
                "source": feed.feed.get("title", url[:40]),
                "published_date": parse_date(entry),
                "raw_text": summary[:1000],
                "category": category,
            })

    except Exception as e:
        print(f"    [ERROR] Failed to fetch {url[:60]}: {e}")

    return items


def fetch_all():
    """Fetch all sources defined in sources.yaml."""
    sources = load_sources()
    all_items = []

    for group_name, feed_list in sources["rss_feeds"].items():
        print(f"    Fetching group: {group_name} ({len(feed_list)} feeds)...")
        for src in feed_list:
            fetched = fetch_rss(src["url"], src["category"])
            all_items.extend(fetched)
            print(f"      → {len(fetched)} items from {src['url'][:50]}")

    return all_items


def deduplicate(items):
    """Remove duplicate items by URL."""
    seen_urls = set()
    seen_titles = set()
    unique = []

    for item in items:
        url_key = item["url"].split("?")[0]  # ignore query params
        title_key = item["title"][:60].lower()

        if url_key not in seen_urls and title_key not in seen_titles:
            seen_urls.add(url_key)
            seen_titles.add(title_key)
            unique.append(item)

    return unique


def filter_recent(items, days=8):
    """Keep only items from the last N days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    return [item for item in items if item["published_date"] >= cutoff]
