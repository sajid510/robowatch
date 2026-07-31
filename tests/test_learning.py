"""Tests for the self-learning memory module."""

from src.learning import LearningMemory


def _item(url="https://example.com/a", title="A", category="research"):
    return {"title": title, "url": url, "category": category}


class TestSeenTracking:
    def test_initial_memory_is_clean(self, tmp_path):
        mem = LearningMemory(path=str(tmp_path / "mem.json"))
        assert mem.stats()["seen_items"] == 0

    def test_record_seen_dedupes(self, tmp_path):
        mem = LearningMemory(path=str(tmp_path / "mem.json"))
        assert mem.record_seen(_item()) is True
        assert mem.record_seen(_item()) is False
        assert mem.is_seen(_item()) is True

    def test_url_query_params_ignored(self, tmp_path):
        mem = LearningMemory(path=str(tmp_path / "mem.json"))
        assert mem.record_seen(_item("https://x.com/a?utm=1")) is True
        assert mem.is_seen(_item("https://x.com/a")) is True

    def test_filter_unseen_marks_new(self, tmp_path):
        mem = LearningMemory(path=str(tmp_path / "mem.json"))
        mem.record_seen(_item("https://x.com/seen"))
        items = [_item("https://x.com/seen"), _item("https://x.com/new")]
        unseen = mem.filter_unseen(items)
        assert len(unseen) == 1
        assert unseen[0]["url"] == "https://x.com/new"

    def test_prune_keeps_cap(self, tmp_path):
        mem = LearningMemory(path=str(tmp_path / "mem.json"))
        for i in range(4500):
            mem.record_seen(_item(f"https://x.com/{i}"))
        assert len(mem.data["seen"]) <= 4000


class TestFeedback:
    def test_weight_application_and_clamp(self, tmp_path):
        mem = LearningMemory(path=str(tmp_path / "mem.json"))
        mem.record_feedback("research", 1)
        mem.record_feedback("research", 1)
        assert mem.data["weights"]["research"] == 2.0
        for _ in range(20):
            mem.record_feedback("industry", 1)
        assert mem.data["weights"]["industry"] == 5.0  # clamped

    def test_parse_feedback_spec(self, tmp_path):
        mem = LearningMemory(path=str(tmp_path / "mem.json"))
        pairs = mem.parse_feedback_spec("research:1, industry:-0.5 ;bad")
        assert ("research", 1.0) in pairs
        assert ("industry", -0.5) in pairs
        assert len(pairs) == 2

    def test_apply_feedback_pairs(self, tmp_path):
        mem = LearningMemory(path=str(tmp_path / "mem.json"))
        applied = mem.apply_feedback_pairs([("cfp", 1.5), ("bangladesh", -1)])
        assert len(applied) == 2
        assert mem.data["weights"]["cfp"] == 1.5
        assert mem.data["weights"]["bangladesh"] == -1.0

    def test_feedback_file(self, tmp_path):
        f = tmp_path / "feedback.txt"
        f.write_text(
            "# comment\n"
            "research,1\n"
            "https://x.com/y,industry,-0.5\n",
            encoding="utf-8",
        )
        mem = LearningMemory(path=str(tmp_path / "mem.json"))
        applied = mem.apply_feedback_file(str(f))
        assert len(applied) == 2
        assert mem.data["weights"]["research"] == 1.0
        assert mem.data["weights"]["industry"] == -0.5


class TestPersonalization:
    def test_note_with_no_prefs(self, tmp_path):
        mem = LearningMemory(path=str(tmp_path / "mem.json"))
        assert "no learned preferences" in mem.personalization_note().lower()

    def test_note_reflects_weights(self, tmp_path):
        mem = LearningMemory(path=str(tmp_path / "mem.json"))
        mem.record_feedback("research", 2)
        mem.record_feedback("fellowship", 1)
        mem.record_feedback("industry", -1)
        note = mem.personalization_note()
        assert "research" in note
        assert "fellowship" in note
        assert "industry" in note  # as de-prioritized

    def test_preferred_categories_ordered(self, tmp_path):
        mem = LearningMemory(path=str(tmp_path / "mem.json"))
        mem.record_feedback("cfp", 3)
        mem.record_feedback("research", 1)
        prefs = mem.preferred_categories(2)
        assert prefs[0][0] == "cfp"


class TestPersistence:
    def test_save_and_reload(self, tmp_path):
        path = str(tmp_path / "mem.json")
        mem = LearningMemory(path=path)
        mem.record_feedback("research", 1.5)
        mem.record_seen(_item())
        mem.note_run(10)
        mem.save()

        reloaded = LearningMemory(path=path)
        assert reloaded.data["weights"]["research"] == 1.5
        assert reloaded.is_seen(_item())
        assert reloaded.stats()["runs"] == 1
        assert reloaded.stats()["items_shown"] == 10

    def test_corrupt_file_starts_fresh(self, tmp_path):
        path = str(tmp_path / "mem.json")
        import pathlib
        pathlib.Path(path).write_text("{not json", encoding="utf-8")
        mem = LearningMemory(path=path)
        assert mem.stats()["seen_items"] == 0
