# 15 — Development Guide

## Environment

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt pytest
```

## Running tests

```bash
python -m pytest tests/ -q
```

All tests are offline: no API keys, no network. The pipeline end-to-end test
uses `--offline` mode. CI (`tests.yml`) runs them on Python 3.10–3.12.

## Code layout conventions

- Each module in `src/` is single-purpose and importable without side effects.
- Item dicts flow through the pipeline unchanged except for enrichment fields.
- Anything that hits the network should degrade gracefully when a key is absent.
- Emoji-heavy `print()` output should tolerate non-UTF-8 consoles (see
  `main()` which reconfigures stdout).

## Adding a new feature

1. **New feed category** → add a group to `config/sources.yaml`.
2. **New report section** → edit `NARRATOR_SYSTEM` and `fallback_builder.py`.
3. **New AI stage** → add a module, call it from `analyze_items`, and provide a
   fallback path + tests.
4. **New CLI flag** → extend `argparse` in `main()` and thread it through
   `run()`.

## Testing guidance

- Pure logic (dedupe, filtering, JSON parsing, fallback rendering, email
  assembly) gets unit tests.
- The pipeline gets one integration test via `run(offline=True, dry_run=True)`.
- Never require live network or keys in tests.

## Committing

```bash
git add -A
git commit -m "feat: describe the change"
git push
```

Update `CHANGELOG.md` and `docs/` for user-facing changes.
