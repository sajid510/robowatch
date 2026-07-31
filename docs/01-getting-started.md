# 01 — Getting Started

## Project Overview

RoboWatch is a scheduled, AI-driven intelligence pipeline for student robotics
teams and researchers. Every Friday it:

1. Pulls ~40 RSS feeds covering robotics news, research, competitions,
   fellowships, conferences, and the Bangladesh robotics scene.
2. Uses **Groq (llama-3.3-70b)** to filter and enrich items with a relevance
   score, priority, deadline, and key-tech tags.
3. Tracks a curated list of **target conferences** (ICRA, IROS, ROBIO, ROSCon,
   IEEE RAAICON, and more) for call-for-papers intelligence.
4. Writes the weekly narrative with **Gemini 2.5 Flash** into a styled
   9-section HTML email.
5. Sends the report to every subscriber via Gmail SMTP.

## Target Audience

- Undergraduate robotics / EEE teams with limited time and budget.
- Students preparing conference papers who need CFP deadlines and venue-fit
  scoring.
- Hobbyists and researchers who want a high-signal weekly robotics digest.

## Features

- Zero-config scheduled runs (GitHub Actions cron).
- Offline demo mode (`--offline`) that needs no API keys or network.
- Dry-run mode that writes `report.html`, `report.json`, `stats.json`.
- Graceful degradation: missing API keys or failed LLM calls never crash the
  pipeline — a deterministic fallback template is used instead.
- Fully configurable feeds, prompts, subscribers, and target conferences.

## System Requirements

- Python 3.10+ (tested on 3.10, 3.11, 3.12, 3.13).
- `pip` for dependency installation.
- Optional: Docker for containerized runs.
- Optional: a Gmail account with an app password for email delivery.

## Prerequisites

- Clone the repository.
- Install dependencies: `pip install -r requirements.txt`.
- For live AI runs: a Groq API key and/or a Gemini API key in environment
  variables. Not required for offline/dry-run demos.

## Repository Structure

See [04 — Project structure](04-project-structure.md).

## Documentation Guide

- [Documentation index](README.md)
- [Installation](02-installation.md)
- [Quick start](03-quick-start.md)

## Support

Open an issue on GitHub, or consult [Troubleshooting](14-troubleshooting.md)
and the [FAQ](13-faq.md).
