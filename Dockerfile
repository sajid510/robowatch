# ── RoboWatch runtime image ────────────────────────────────────────────────
# Multi-stage build keeps the final image lean (no build tooling).
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# ── Dependencies ───────────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Application ────────────────────────────────────────────────────────────
COPY src/ src/
COPY config/ config/
COPY subscribers.txt .

# Sanity check: the pipeline must start and import cleanly.
RUN python -c "import src.main; print('RoboWatch imports OK')"

# Run a quick offline smoke test at build time to catch regressions early.
RUN python -m src.main --offline --dry-run --output-dir /tmp/smoke && \
    test -s /tmp/smoke/report.html

# The weekly report is generated on a schedule by GitHub Actions; the image
# is provided for local runs, self-hosting, or embedding in your own CI.
ENTRYPOINT ["python", "-m", "src.main"]
CMD ["--offline", "--dry-run"]
