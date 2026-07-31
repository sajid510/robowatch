"""Tests for the structured fallback report builder (used when Gemini fails)."""

from datetime import datetime, timezone

from src.fallback_builder import build_fallback_report


def _item(**overrides):
    item = {
        "title": "Test title",
        "url": "https://example.com/x",
        "source": "Test source",
        "published_date": datetime.now(timezone.utc),
        "raw_text": "snippet",
        "category": "industry",
        "summary": "summary text",
        "score": 8,
        "priority": "MEDIUM",
        "reasoning": "why it matters",
        "bd_relevant": False,
        "deadline": None,
        "key_tech": ["ROS2"],
    }
    item.update(overrides)
    return item


class TestBuildFallbackReport:
    def test_empty_items_produce_no_sections(self):
        html = build_fallback_report([])
        assert html == ""

    def test_renders_section_heading(self):
        html = build_fallback_report([_item(category="research")])
        assert "Research Spotlight" in html

    def test_renders_cfp_tracker_section(self):
        html = build_fallback_report([_item(category="cfp")])
        assert "Paper Submission Tracker" in html

    def test_renders_high_priority_alert(self):
        html = build_fallback_report([_item(priority="HIGH")])
        assert "This week's highlights" in html

    def test_renders_action_checklist(self):
        html = build_fallback_report([_item(priority="HIGH")])
        assert "Action Checklist" in html

    def test_renders_quick_scan_for_low(self):
        html = build_fallback_report([_item(priority="LOW")])
        assert "Quick Scan" in html

    def test_renders_deadline_in_meta(self):
        html = build_fallback_report([_item(deadline="2026-08-01")])
        assert "2026-08-01" in html

    def test_renders_bd_flag(self):
        html = build_fallback_report([_item(bd_relevant=True)])
        assert "BD Eligible" in html
