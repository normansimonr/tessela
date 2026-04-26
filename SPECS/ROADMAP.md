# Project Roadmap

## Phase 1: Foundation (Current)
- [x] Initial data ingestion for Masoretic, LXX, and Vulgate.
- [ ] Integration of Qumran (Dead Sea Scrolls) textual data.
- [x] Implementation of semantic normalization (decomposition).
- [x] Implementation of semantic comparison logic.
- [x] Integration of Qere-Ketiv and CTAT OCR results.

## Phase 2: Pipeline Refactoring (Immediate Priority)
Transition the current disorganized scripts into a strict sequence of stages. Each stage will produce its own SQLite database to allow for modularity and easy re-runs of specific parts of the process.

- **Stage 0: Ingestion**
  - Input: Raw CSVs/SQLs from `data/raw` (MT, LXX, Vulgate, Qumran).
  - Output: `tessela_0_raw.db`
- **Stage 1: Alignment**
  - Input: `tessela_0_raw.db` + mapping scripts.
  - Output: `tessela_1_aligned.db` (versification mapping completed).
- **Stage 2: Normalization**
  - Input: `tessela_1_aligned.db` + Gemini 3.1 Flash Lite API.
  - Output: `tessela_2_normalised.db` (atomic propositions added).
- **Stage 3: Comparison**
  - Input: `tessela_2_normalised.db` + Gemini 3.1 Flash Lite API.
  - Output: `tessela_3_compared.db` (semantic differences flagged).

## Phase 3: Validation & Tooling
- [ ] Automated testing for normalization accuracy.
- [ ] CLI tool to "jump" into any stage of the pipeline.
- [ ] Export scripts for scholarly publishing (Markdown/PDF).
