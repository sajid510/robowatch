import feedparser
import re
from datetime import datetime, timezone, timedelta
import yaml
from pathlib import Path

_PUNCT = re.compile(r"[^\w\s]")


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


def _title_key(title):
    """Normalize a title for near-duplicate detection."""
    return _PUNCT.sub(" ", title.lower()).strip()


def deduplicate(items):
    """Remove duplicate items by URL and near-duplicate titles.

    Two titles count as duplicates when one is a prefix of the other and the
    longer one is at least 20 characters, which catches reposts that append
    suffixes such as "— update" or ", part 2" while keeping distinct headlines.
    """
    seen_urls = set()
    seen_titles = []
    unique = []

    for item in items:
        url_key = item["url"].split("?")[0]  # ignore query params
        title_key = _title_key(item["title"])

        prefix_dup = False
        for seen in seen_titles:
            if len(title_key) >= 20 and (title_key.startswith(seen) or seen.startswith(title_key)):
                prefix_dup = True
                break

        if url_key not in seen_urls and not prefix_dup:
            seen_urls.add(url_key)
            seen_titles.append(title_key)
            unique.append(item)

    return unique


def filter_recent(items, days=8):
    """Keep only items from the last N days (items without dates are kept)."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    return [item for item in items if item.get("published_date", cutoff) >= cutoff]
