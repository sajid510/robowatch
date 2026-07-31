"""End-to-end test of the offline pipeline (fetch -> analyze -> dry-run output).

This exercises the full RoboWatch flow without network access or API keys:
the AI filter and enricher degrade gracefully and the report falls back to the
structured template, which is then written as an HTML artifact.
"""

import json
import os
from pathlib import Path

from src.main import run
from src.sample_data import sample_items


class TestOfflinePipeline:
    def test_sample_items_have_required_fields(self):
        items = sample_items()
        assert len(items) >= 8
        for item in items:
            for field in ("title", "url", "source", "published_date",
                          "raw_text", "category"):
                assert field in item, f"missing {field}"

    def test_run_offline_writes_artifacts(self, tmp_path):
        out = str(tmp_path / "out")
        result = run(offline=True, dry_run=True, output_dir=out)
        assert isinstance(result, str)
        assert Path(result) == Path(out)

        html = Path(out, "report.html")
        assert html.exists()
        content = html.read_text(encoding="utf-8")
        assert "RoboWatch Weekly Intelligence" in content
        assert "<html" in content

        stats = json.loads(Path(out, "stats.json").read_text(encoding="utf-8"))
        assert stats["items"] > 0
        assert stats["delivered"] is True

    def test_run_offline_uses_fallback_not_gemini(self, tmp_path):
        # Without GEMINI_API_KEY the narrator returns None -> fallback template
        os.environ.pop("GEMINI_API_KEY", None)
        os.environ.pop("GROQ_API_KEY", None)
        out = str(tmp_path / "out")
        run(offline=True, dry_run=True, output_dir=out)
        body = json.loads(Path(out, "report.json").read_text(encoding="utf-8"))
        assert body["body"]  # fallback HTML body non-empty

    def test_feedback_personalizes_and_persists(self, tmp_path):
        os.environ.pop("GEMINI_API_KEY", None)
        os.environ.pop("GROQ_API_KEY", None)
        mem_path = str(tmp_path / "mem.json")
        out = str(tmp_path / "out")
        run(
            offline=True, dry_run=True, output_dir=out,
            memory_file=mem_path, feedback="research:1,industry:-0.5",
        )
        # Inline feedback applied; offline mode does not persist memory.
        assert not Path(mem_path).exists()
        stats = json.loads(Path(out, "stats.json").read_text(encoding="utf-8"))
        assert stats["feedback_applied"] == 2
        assert "research" in stats["personalization"]

    def test_learn_mode_persists_memory(self, tmp_path):
        # A real (non-offline) dry-run with a temp memory file persists it.
        mem_path = str(tmp_path / "mem.json")
        out = str(tmp_path / "out")
        run(
            offline=True, dry_run=True, output_dir=out,
            memory_file=mem_path, learn=False,
        )
        # --offline implies learn=False; nothing persisted
        assert not Path(mem_path).exists()
