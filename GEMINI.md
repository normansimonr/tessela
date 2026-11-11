# Tessela Development Guidelines

## Project constitution (source of truth)
- `SPECS/MISSION.md` — mission and vision
- `SPECS/TECH.md` — stack and architecture (pipeline stages, SQLite outputs)
- `SPECS/ROADMAP.md` — phases and priorities
- `README.md` — developer-facing setup and usage

## Stack
- Python 3.11+
- Google Gemini 3.1 Flash Lite (`google-generativeai`) for normalization/comparison
- SQLite 3 for pipeline stage databases
- Data/OCR: pandas, PyMuPDF (fitz), Pillow, pytesseract as needed
- `GOOGLE_API_KEY` required for AI services

## Structure (high level)
- `src/` — application/source modules (e.g. data loading, normalization service)
- `scripts/` — executable pipeline scripts (e.g. `run_normalization.py`, `run_comparison.py`)
- `prompts/` — AI prompt templates
- `data/` — input/raw/intermediate datasets
- `SPECS/` — mission, tech, roadmap, and feature specs

## Common commands
- `./run.sh` — run normalization pipeline (see README prerequisites/env)
- `./compare.sh` — run comparison workflow
- `./prepare_database.sh` — prepare/build SQLite database from data sources
- `python -m pytest` — run tests if/when a test suite exists

## Conventions
- Follow the pipeline-driven architecture in `SPECS/TECH.md` (stage inputs/outputs as SQLite DBs).
- Keep behaviour aligned with the constitution; update `SPECS/*` and `README.md` when implementation changes shipped reality.
