# Tasks: Biblical Text Normalizer

**Input**: Design documents from `tessela/.specify/`
**Prerequisites**: `plan-biblical-text-normalizer.md`, `feature-biblical-text-normalizer.md`

## Phase 1: Setup

**Purpose**: Project initialization and basic structure.

- [ ] T001 Create the project directories: `src`, `tests`, `scripts`, `output`, `prompts`.
- [ ] T002 Create an empty `__init__.py` in `src/` and `tests/`.
- [ ] T003 Create `prompts/normalization_prompt.txt` with a placeholder prompt.
- [ ] T004 Create `requirements.txt` and add `pandas` and `google-generativeai`.
- [ ] T005 Create an empty `.gitkeep` file in the `output/` directory.

---

## Phase 2: User Story 1 - Generate a Normalized Dataset (Priority: P1) 🎯 MVP

**Goal**: Process source texts and generate a set of normalized CSV files.

**Independent Test**: Run the main script and verify that the three normalized CSV files are created correctly in the `output/` directory.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T006 [P] [US1] Create `tests/test_data_loader.py` with tests for loading CSVs and handling file-not-found errors.
- [ ] T007 [P] [US1] Add tests to `tests/test_data_loader.py` for the Septuagint filtering logic.
- [ ] T008 [P] [US1] Create `tests/test_normalization_service.py` with a mocked test for the AI normalization service, ensuring it handles API responses correctly.

### Implementation for User Story 1

- [ ] T009 [US1] Implement the data loading function in `src/data_loader.py`.
- [ ] T010 [US1] Implement the Septuagint filtering function in `src/data_loader.py`.
- [ ] T011 [US1] Implement the normalization service in `src/normalization_service.py`, ensuring it loads the prompt from `prompts/normalization_prompt.txt` and the API key from environment variables.
- [ ] T012 [US1] Create the main orchestration script `scripts/run_normalization.py`.
- [ ] T013 [US1] Implement the main logic in `scripts/run_normalization.py` to load data, iterate through rows, call the normalization service, and add the new `normalization` column.
- [ ] T014 [US1] Add logic to `scripts/run_normalization.py` to save the processed dataframes to `masoretic_normalised.csv`, `vulgate_normalised.csv`, and `septuagint_normalised.csv` in the `output/` directory.
- [ ] T015 [P] [US1] Add `tqdm` or simple print statements to `scripts/run_normalization.py` for progress indication.

---

## Phase 3: Polish & Cross-Cutting Concerns

**Purpose**: Final packaging and documentation.

- [ ] T016 Create the `Dockerfile` to containerize the Python application.
- [ ] T017 Update the `README.md` with a full description of the tool and detailed instructions for building and running it via Docker.

---

## Dependencies & Execution Order

- **Phase 1 (Setup)** must be completed first.
- **Phase 2 (User Story 1)** depends on Phase 1.
  - Within Phase 2, tests (T006-T008) should be written before implementation tasks (T009-T015).
- **Phase 3 (Polish)** can be completed after Phase 2.
