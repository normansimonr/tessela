# Project Roadmap: Tessela

This roadmap tracks delivery against `SPECS/MISSION.md`. It has two cycles:

1. **Current cycle — repository readiness (immediate priority).** Make the repo
   legible, demonstrable, and visibly rigorous so a reviewer can understand and
   trust it in minutes.
2. **Next dev cycle — research roadmap (deferred).** The full research and
   pipeline programme. Nothing here is abandoned; it is intentionally deferred
   until the readiness cycle is complete.

---

# Current cycle: Repository readiness (IMMEDIATE PRIORITY)

## Goal

Make the repository reviewer-ready: a five-minute reviewer experience, a working
vertical slice, visible engineering rigor, and clear evidence of engineering
judgment. This cycle takes precedence over all research-roadmap work.

## Target five-minute reviewer experience

1. **README** that says what it is, shows a screenshot/GIF, gives a three-command
   quickstart, and includes a Mermaid architecture diagram and a status table.
2. **A working vertical slice**: `tessela dossier "DEU 32:8"` prints the MT, SP
   and DSS readings and the differences.
3. **Green CI badge** (ruff + mypy + pytest) and a real test suite.
4. **Recent commits, open issues, a project board, and 1–2 PRs** — evidence of
   active development.
5. **`docs/decisions/`** with short ADRs showing engineering trade-offs.

## P0 — Fix the first impression (COMPLETE)

- [x] Make the repo public; description, topics and demo set.
- [x] README overhaul:
  - one-sentence pitch and a concrete example (Deut 32:8: MT “sons of
    Israel” vs 4Q37 “sons of God”);
  - terminal demo output (`make demo`) — a rendered GIF can be added later;
  - Mermaid architecture diagram (Stage 0 → 7);
  - “Current status” and “What it does — and what is planned” tables;
  - three-command quickstart;
  - “Why this exists” and data/licensing sections.
- [x] Add CI (`.github/workflows/ci.yml`) running `ruff`, `mypy` and `pytest`;
      badge added to the README.
- [x] Add `pyproject.toml` with `[tool.ruff]`, `[tool.mypy]` and
      `[tool.pytest.ini_options]`.
- [x] Add a `Makefile` (`make install`, `make install-dev`, `make test`,
      `make lint`, `make check`, `make demo`).
- [x] Add GitHub topics (`biblical-studies`, `textual-criticism`,
      `dead-sea-scrolls`, `septuagint`, `hebrew-bible`, `nlp`, `python`, `ai`).
- [x] Add `src/witnesses.py` + `scripts/demo.py` (a first, data-only vertical
      slice used by `make demo`).
- [x] Add `DATA_LICENSES.md` separating the MIT code licence from the dataset
      licences.

## P1 — Build the vertical slice (the single most compelling thing)

The repo currently has strong data and docs but a thin code layer. A small,
working end-to-end feature changes the story from “ambitious vision” to
“working system”.

- [ ] Implement a `tessela` CLI with a `dossier` command:
  - load MT (`data/reference/versification/leningrad_codex.csv`), SP
    (`samaritan.csv`) and DSS (`qumran.csv`) for a reference;
  - normalise (remove points/cantillation, maqaf → space, punctuation);
  - print a side-by-side comparison with the differences highlighted;
  - emit a Markdown dossier with provenance and a short assessment.
- [ ] Add `examples/` with 2–3 rendered dossiers (Gen 2:2, Deut 27:4,
      Deut 32:8) so a reviewer can see the output without running anything.
- [ ] Add tests for the slice: happy path, missing verse, multi-scroll DSS,
      and a lacuna.
- [ ] Refactor the core AI code:
  - replace `print()` with structured logging;
  - fix the `gemini-2.0-flash` mismatch (TECH.md specifies Gemini 3.1 Flash
    Lite; make the model configurable);
  - remove bare `except Exception: return []` paths;
  - add type hints and a typed response model;
  - inject the model client so it can be tested with a fake.

## P2 — Show engineering judgment

- [ ] Add 3–5 short ADRs under `docs/decisions/`:
  - `0001-sqlite-stage-pipeline.md` (why stage-gated SQLite and immutable
    outputs);
  - `0002-provenance-and-attested-vs-reconstructed.md`;
  - `0003-ai-model-choice-and-evaluation.md`;
  - `0004-data-licensing-and-distribution.md`;
  - `0005-why-not-a-graph-database-yet.md`.
- [ ] Create 8–10 well-scoped issues from this roadmap (“Implement Stage 0
      ingestion”, “Add `dossier` CLI”, “Add CI”, “Fix model mismatch”, “Add
      Peshitta ingestion”, “Add evaluation harness”, etc.) with labels
      (`good first issue`, `enhancement`, `data`, `ai`) and a project board.
- [ ] Work on feature branches and open PRs (even self-merged) rather than
      committing directly to `master`.
- [ ] Add `docs/ai-workflow.md` explaining the spec-driven, agent-assisted loop
      (plan → implement → review → verify), Red/Green TDD, and how AI responses
      are evaluated.
- [ ] Add an evaluation harness: a small labelled set of variants (significant
      vs. not) and a script that reports agreement (even a simple confusion
      matrix).

## P3 — Polish

- [ ] Add `CITATION.cff`, `CONTRIBUTING.md`, `SECURITY.md`,
      `CODE_OF_CONDUCT.md`.
- [ ] Add `DATA_LICENSES.md` clarifying that the code is MIT while the imported
      data has separate licences (STEPBible SP, ETCBC/dss CC BY-NC 4.0, CTAT
      page references, etc.).
- [ ] Tag a release (`v0.1.0`) with release notes.
- [ ] Address repo size: consider Git LFS or a `make data` download script for
      the large datasets (`bible.db`, `tov_flagged.csv`, etc.).

## Risks to address in this cycle

- **Licensing mismatch:** the code is MIT, but the Samaritan text is
  “Copyrighted; Free non-commercial distribution” and the DSS dataset is
  CC BY-NC 4.0. Decide deliberately: keep restricted texts out of a public
  repo, add `DATA_LICENSES.md`, or keep the repo private with reviewer access.
- **Private repo:** ensure the reviewer can access it.
- **Overclaiming:** the mission is ambitious; the README must show a credible
  working slice and a clear “what’s next”, not just a grand vision.
- **Stale scripts:** `run.sh`, `compare.sh` and `src/normalization_service.py`
  still reflect the old CSV flow and model. Refactor or mark them clearly as
  legacy.

## Seven-day plan

| Day | Focus |
|---|---|
| 1 | Make repo public; README overhaul; CI + `pyproject.toml` + `Makefile` |
| 2–3 | Build `tessela dossier` vertical slice; add `examples/` |
| 4 | Tests for the slice; refactor AI client (logging, model config, typed responses) |
| 5 | ADRs; create issues + project board; open 1–2 PRs |
| 6 | Screenshots/GIF; `docs/ai-workflow.md`; data licensing note |
| 7 | Tag `v0.1.0`; final README polish; release notes |

---

# Next dev cycle: Research roadmap (DEFERRED)

> **Deferred until the repository-readiness cycle is complete.** The phases below
> are the next development cycle, not the current priority.

## Phase 0: Constitution & tooling (Done)

- [x] Establish mission, tech spec, and roadmap
- [x] Align OpenCode config and dev guidelines with Tessela
- [x] Update mission to full research-assistant vision

---

## Phase 1: Foundation (In progress)

### 1.1 Data ingestion (partial)
- [x] Initial data ingestion for Masoretic (JPS 1917 English), LXX (Brenton English), Vulgate (DRA English)
- [x] Tov's LXX retroversion processing (word-level → verse-level boolean flag)
- [x] Qere/Ketiv extraction from STEP-Bible TAHOT (standalone scripts)
- [x] CTAT OCR pipeline (PDF → images → OCR → verse/page mapping)
- [x] Import textual-criticism datasets: Qumran (125 DSS references), Samaritan Pentateuch (33 references), Masoretic minority (1), enriched Qere/Ketiv (1,013 words / 837 verses with morphology, roots, readings), CTAT/HOTTP `refs.csv` (3,348 verses), Tov Septuagint corpus (`tov_flagged.csv`, 12,951 variants; 42 raw `.par` files, git-ignored per licensing policy; normalisation tables), Leningrad codex versification (23,213 verses), and book catalog (66 books) — see `data/README.md`
- [x] Import and adapt the textual-criticism generator scripts: `scripts/qere-ketiv` (+ `scripts/qere_ketiv/`), `scripts/ctat-refs` (+ `scripts/ctat/`), `scripts/lxx-refs` (+ `scripts/lxx/`), with their tests; verified to reproduce the imported datasets (`./scripts/lxx-refs build`, `./scripts/ctat-refs refs`, Qere/Ketiv analyser)
- [ ] Integrate the imported DSS/SP/CTAT/Septuagint data into the stage-gated pipeline (data is imported; pipeline wiring pending)
- [x] Samaritan Pentateuch Hebrew text imported for the 33 curated variants (the `hebrew_text` column of `data/manual_datasets/samaritan/samaritan.csv`, STEPBible SP; credited in `samaritan/README.md`)
- [ ] Samaritan Pentateuch enrichment beyond the Hebrew text: variant descriptions, alignment notes, and integration into the variant dataset
- [x] Dead Sea Scrolls Hebrew readings imported for the 125 curated passages (`qumran.csv`: one row per passage and scroll, with clean text and ETCBC transcription; ETCBC/dss 2.0.5, CC BY-NC 4.0; credited in `qumran/README.md`)
- [ ] Dead Sea Scrolls enrichment beyond the Hebrew readings: alignment notes, variant descriptions, and integration into the variant dataset
- [ ] Peshitta data ingestion
- [ ] Integrate Qere/Ketiv into main pipeline with morphology/roots
- [ ] Integrate CTAT OCR/refs output into variant evaluation

### 1.2 Semantic normalization (done)
- [x] Implementation of semantic normalization (atomic propositions via Gemini)
- [x] Implementation of semantic comparison logic (binary + justification)

### 1.3 Known issues to resolve
- [ ] Fix AI model mismatch: code uses `gemini-2.0-flash`; TECH.md specifies Gemini 3.1 Flash Lite
- [ ] Replace `print()`-based error handling with structured logging
- [ ] Add provenance/uncertainty fields to data model

---

## Phase 2: Pipeline refactoring

Transition the current disorganized scripts into a strict sequence of stages.
Each stage produces its own SQLite database for modularity and easy re-runs.

- **Stage 0: Ingestion**
  - Input: Raw CSVs/SQLs from `data/raw` (MT, LXX, Vulgate, Qumran, SP, Peshitta) + manual datasets + CTAT OCR
  - Output: `tessela_0_raw.db`
  - Schema: unified, source-aware, with provenance, evidence kind (attested/reconstructed/secondary), uncertainty, missing-data markers
  - Must include: Hebrew MT text, Qere/Ketiv with morphology, Tov retroversions with full chain, SP/DSS variant descriptions, Vulgate/Peshitta data, CTAT page mappings

- **Stage 1: Alignment**
  - Input: `tessela_0_raw.db` + mapping scripts
  - Output: `tessela_1_aligned.db`
  - Versification mapping across witnesses; handle combined/omitted/reordered verses
  - Record alignment confidence and uncertainty
  - Do not rely solely on chapter/verse number matching

- **Stage 2: Normalization**
  - Input: `tessela_1_aligned.db` + Gemini API
  - Output: `tessela_2_normalised.db`
  - Atomic propositions per reading (all witnesses, not just MT/LXX/Vulgate)
  - Preserve reading provenance

- **Stage 3: Comparison**
  - Input: `tessela_2_normalised.db` + Gemini API
  - Output: `tessela_3_compared.db`
  - Semantic differences flagged with 3-level significance (formal / semantic / interpretive)
  - Preserve reasoning (not just binary label)

- **Stage 4: Scholarly retrieval**
  - Input: `tessela_3_compared.db` + CTAT PDFs + open-access paper sources
  - Output: `tessela_4_sourced.db`
  - Retrieve CTAT discussion by page reference; extract arguments with citations
  - Search and link open-access papers; respect copyright/licensing
  - Distinguish quotations, paraphrases, and system conclusions

- **Stage 5: Hypothesis generation**
  - Input: `tessela_4_sourced.db`
  - Output: `tessela_5_hypotheses.db`
  - Directed graphs/trees of textual development
  - Nodes = readings/textual states; edges = proposed changes with mechanism, probability, evidence
  - Encode scribal/translational tendencies as explicit considerations
  - Generate competing (alternative) models
  - Systematic exploration of materially distinct hypotheses

- **Stage 6: Adversarial analysis**
  - Input: `tessela_5_hypotheses.db` + Gemini API
  - Output: `tessela_6_assessed.db`
  - Monica (MT advocate), Tomás (challenger), Ernesto (adjudicator)
  - All agents grounded in dataset/sources; cite specific readings and references
  - Calibrated conclusions; preserve uncertainty

- **Stage 7: Dossier export**
  - Input: `tessela_6_assessed.db`
  - Output: Research dossiers (Markdown/PDF) per significant variant
  - Include all elements from Mission §10

### Additional Phase 2 tasks
- [ ] CLI tool to jump into any stage of the pipeline
- [ ] LXX retroversion chain preservation (Greek → Hebrew Vorlage → reasoning → uncertainty → alternatives)
- [ ] Vulgate and Peshitta retroversion investigation (labeled as reconstructions)

---

## Phase 3: Validation & tooling

- [ ] Automated testing for normalization accuracy and pipeline correctness
- [ ] Automated testing for alignment, comparison, and hypothesis generation
- [ ] Export scripts for scholarly publishing (Markdown/PDF dossiers)
- [ ] Reproducibility/inspectability: record inputs, outputs, model, config for all AI steps
- [ ] Uncertainty visualization in dossiers
- [ ] Researcher correction workflow (correct a reading/alignment, add source, rerun analysis)

---

## Phase 4: Advanced capabilities (Long-term)

- [ ] Hypothesis graph visualization (interactive)
- [ ] Additional scholarly literature integration (beyond CTAT)
- [ ] Improved original-language alignment (Hebrew/Greek/Latin/Syriac)
- [ ] More advanced hypothesis modelling and scoring
- [ ] Translation-focused views (how variant affects translation choices)
- [ ] Multi-user collaboration support

---

## Witness coverage tracker

| Witness | Ingestion | Alignment | Normalization | Comparison | Hypotheses | Status |
|---|---|---|---|---|---|---|
| Masoretic Text | Partial (English JPS; Hebrew in Tov CSV) | Partial | ✅ | ✅ | ❌ | In progress |
| Qere/Ketiv | ✅ (1,013 words / 837 verses, with morphology & roots) | ❌ | ❌ | ❌ | ❌ | Data imported; needs integration |
| Samaritan Pentateuch | ✅ (33 references + SP Hebrew text) | ❌ | ❌ | ❌ | ❌ | Hebrew text imported; needs integration |
| Dead Sea Scrolls | ✅ (125 passages / 199 readings, with Hebrew text) | ❌ | ❌ | ❌ | ❌ | Hebrew readings imported; needs integration |
| Septuagint (Tov) | ✅ (`tov_flagged.csv`, 12,951 variants; 42 `.par` files) | Partial | Partial (normalisation tables) | ❌ | ❌ | Data imported; needs chain preservation |
| Vulgate | Partial (English DRA) | Partial | ❌ | ❌ | ❌ | Needs retroversion pipeline |
| Peshitta | ❌ | ❌ | ❌ | ❌ | ❌ | Not started |
| CTAT | ✅ (`refs.csv`, 3,348 verses + OCR pipeline) | ❌ | N/A | N/A | ❌ | Data imported; needs integration |

---

## Key principles (from Mission §8)

1. Evidence before conclusions.
2. Preserve attested vs. reconstructed distinction throughout.
3. Preserve provenance and traceability.
4. Make uncertainty explicit.
5. Treat witnesses critically.
6. Distinguish textual evidence from interpretation.
7. Avoid predetermined outcomes.
8. Be reproducible and inspectable.
9. Keep the researcher in control.
