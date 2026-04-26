# Project Roadmap

## Phase 1: Foundation (Current)
- [x] Initial data ingestion for Masoretic, LXX, and Vulgate.
- [ ] Integration of Qumran (Dead Sea Scrolls) textual data.
- [x] Implementation of semantic normalization (decomposition).
- [x] Implementation of semantic comparison logic.
- [x] Integration of Qere-Ketiv and CTAT OCR results.

## Phase 2: Pipeline Refactoring (Immediate Priority)
Transition the current disorganized scripts into a strict sequence of stages. Each stage will produce its own SQLite database to allow for modularity and easy re-runs of specific parts of the process.

- **Stage 0: Ingestion** (`pipeline/stage_0/`)
  - Input: `pipeline/original_data/`
  - Output: `pipeline/stage_0/tessela_0_raw.db`
- **Stage 1: Alignment** (`pipeline/stage_1/`)
  - Input: `pipeline/stage_0/tessela_0_raw.db`
  - Output: `pipeline/stage_1/tessela_1_aligned.db` (versification mapping completed).
- **Stage 2: Normalization** (`pipeline/stage_2/`)
  - Input: `pipeline/stage_1/tessela_1_aligned.db`
  - Output: `pipeline/stage_2/tessela_2_normalised.db` (atomic propositions added).
- **Stage 3: Comparison** (`pipeline/stage_3/`)
  - Input: `pipeline/stage_2/tessela_2_normalised.db`
  - Output: `pipeline/stage_3/tessela_3_compared.db` (semantic differences flagged).

## Phase 3: Validation & Tooling
- [ ] Automated testing for normalization accuracy.
- [ ] CLI tool to "jump" into any stage of the pipeline.
- [ ] Export scripts for scholarly publishing (Markdown/PDF).
