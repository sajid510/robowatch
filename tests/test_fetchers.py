"""Tests for the RSS fetching, deduplication and recency filtering logic."""

import time
from datetime import datetime, timezone, timedelta
from types import SimpleNamespace

from src.fetchers import (
    load_sources,
    parse_date,
    fetch_rss,
    deduplicate,
    filter_recent,
)


def _item(url, title, published=None):
    return {
        "title": title,
        "url": url,
        "source": "test",
        "published_date": published or datetime.now(timezone.utc),
        "raw_text": "snippet",
        "category": "industry",
    }


class TestDeduplicate:
    def test_removes_duplicate_urls(self):
        items = [
            _item("https://example.com/a?utm_source=1", "Title A"),
            _item("https://example.com/a", "Title A"),
        ]
        assert len(deduplicate(items)) == 1

    def test_removes_duplicate_titles(self):
        items = [
            _item("https://example.com/1", "Same headline here"),
            _item("https://example.com/2", "Same headline here, slightly longer"),
        ]
        assert len(deduplicate(items)) == 1

    def test_removes_suffixed_repost(self):
        items = [
            _item("https://example.com/1", "Robot Uses SLAM to Navigate Hospitals"),
            _item("https://example.com/2", "Robot Uses SLAM to Navigate Hospitals — update"),
        ]
        assert len(deduplicate(items)) == 1

    def test_keeps_short_distinct_prefixes(self):
        # Short titles that merely share a prefix must NOT collapse
        items = [
            _item("https://example.com/1", "SLAM"),
            _item("https://example.com/2", "SLAM robot"),
        ]
        assert len(deduplicate(items)) == 2

    def test_keeps_distinct_items(self):
        items = [
            _item("https://example.com/1", "Headline one"),
            _item("https://example.com/2", "Headline two"),
            _item("https://example.com/3", "Headline three"),
        ]
        assert len(deduplicate(items)) == 3


class TestFilterRecent:
    def test_keeps_recent_drops_old(self):
        now = datetime.now(timezone.utc)
        recent = _item("https://example.com/1", "Recent", published=now - timedelta(days=2))
        old = _item("https://example.com/2", "Old", published=now - timedelta(days=30))
        result = filter_recent([recent, old], days=8)
        assert len(result) == 1
        assert result[0]["title"] == "Recent"

    def test_empty_list(self):
        assert filter_recent([], days=8) == []

    def test_keeps_item_without_date(self):
        item = _item("https://example.com/1", "No date", published=None)
        assert filter_recent([item], days=8) == [item]


class TestParseDate:
    def test_uses_published_parsed(self):
        entry = SimpleNamespace(
            published_parsed=time.struct_time((2026, 1, 5, 10, 30, 0, 0, 0, 0)),
            updated_parsed=time.struct_time((2026, 1, 6, 10, 30, 0, 0, 0, 0)),
        )
        assert parse_date(entry).year == 2026
        assert parse_date(entry).day == 5

    def test_falls_back_to_updated(self):
        entry = SimpleNamespace(
            published_parsed=None,
            updated_parsed=time.struct_time((2026, 2, 10, 1, 2, 3, 0, 0, 0)),
        )
        assert parse_date(entry).day == 10

    def test_defaults_to_now(self):
        entry = SimpleNamespace(published_parsed=None, updated_parsed=None)
        assert abs((parse_date(entry) - datetime.now(timezone.utc)).total_seconds()) < 5


class TestFetchRss:
    def test_invalid_url_returns_empty(self):
        assert fetch_rss("not-a-valid-url", "industry") == []

    def test_load_sources_has_feeds(self):
        sources = load_sources()
        assert "rss_feeds" in sources
        assert len(sources["rss_feeds"]) > 0
