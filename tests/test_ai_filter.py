"""Tests for the AI relevance-filter JSON parsing helper."""

from src.ai_filter import parse_json_response


class TestParseJsonResponse:
    def test_none_returns_none(self):
        assert parse_json_response(None) is None

    def test_empty_returns_none(self):
        assert parse_json_response("") is None

    def test_plain_json_array(self):
        raw = '[{"index": 0, "keep": true, "reason": "relevant"}]'
        result = parse_json_response(raw)
        assert result == [{"index": 0, "keep": True, "reason": "relevant"}]

    def test_markdown_fenced(self):
        raw = '```json\n[{"index": 1, "keep": false, "reason": "off topic"}]\n```'
        result = parse_json_response(raw)
        assert result[0]["index"] == 1
        assert result[0]["keep"] is False

    def test_strips_surrounding_text(self):
        raw = 'Sure, here you go:\n\n[{"index": 0, "keep": true, "reason": "ok"}]\n\nHope this helps.'
        result = parse_json_response(raw)
        assert len(result) == 1
        assert result[0]["keep"] is True

    def test_invalid_json_returns_none(self):
        assert parse_json_response("[not valid json") is None

    def test_no_array_returns_none(self):
        assert parse_json_response("just some words") is None
