"""Tests for the mailer: subscriber parsing and email HTML assembly."""

import os
from src.mailer import load_subscribers, build_email


class TestLoadSubscribers:
    def test_parses_valid_emails(self, tmp_path):
        p = tmp_path / "subscribers.txt"
        p.write_text(
            "# comment\n"
            "a@example.com\n"
            "\n"
            "b@example.com  \n"
            "not-an-email\n",
            encoding="utf-8",
        )
        old = os.getcwd()
        os.chdir(tmp_path)
        try:
            emails = load_subscribers()
        finally:
            os.chdir(old)
        assert emails == ["a@example.com", "b@example.com"]

    def test_missing_file_returns_empty(self, tmp_path):
        old = os.getcwd()
        os.chdir(tmp_path)
        try:
            assert load_subscribers() == []
        finally:
            os.chdir(old)


class TestBuildEmail:
    def test_wraps_body_with_css_and_count(self):
        html = build_email("<h2>Hello</h2>", item_count=3)
        assert "<html lang=\"en\">" in html
        assert "<style>" in html
        assert "<h2>Hello</h2>" in html
        assert "3 items tracked" in html

    def test_escapes_placeholders_are_substituted(self):
        html = build_email("body", item_count=0)
        assert "{body}" not in html
        assert "{count}" not in html
