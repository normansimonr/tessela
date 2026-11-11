# Project Roadmap: Tessela

This roadmap tracks delivery against `SPECS/MISSION.md`. Phases are ordered by
dependency: a reliable, source-aware dataset and alignment come before semantic
evaluation, which comes before hypothesis generation and adversarial analysis.

---

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
- [ ] Integration of Qumran (Dead Sea Scrolls) textual data (~150 curated variants)
- [ ] Samaritan Pentateuch enrichment (Hebrew text + descriptions for ~20 variants)
- [ ] Peshitta data ingestion
- [ ] Integrate Qere/Ketiv into main pipeline with morphology/roots
- [ ] Integrate CTAT OCR output into variant evaluation

### 1.2 Semantic normalization (done)
- [x] Implementation of semantic normalization (atomic propositions via Gemini)
- [x] Implementation of semantic comparison logic (binary + justification)

### 1.3 Known issues to resolve
- [ ] Fix AI model mismatch: code uses `gemini-2.0-flash`; TECH.md specifies Gemini 3.1 Flash Lite
- [ ] Replace `print()`-based error handling with structured logging
- [ ] Add provenance/uncertainty fields to data model

---

## Phase 2: Pipeline refactoring (Immediate priority)

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
| Qere/Ketiv | ✅ (standalone) | ❌ | ❌ | ❌ | ❌ | Not integrated |
| Samaritan Pentateuch | Partial (verse refs only) | ❌ | ❌ | ❌ | ❌ | Needs enrichment |
| Dead Sea Scrolls | ❌ | ❌ | ❌ | ❌ | ❌ | Not started |
| Septuagint (Tov) | ✅ (word-level) | Partial | ❌ | ❌ | ❌ | Needs chain preservation |
| Vulgate | Partial (English DRA) | Partial | ❌ | ❌ | ❌ | Needs retroversion pipeline |
| Peshitta | ❌ | ❌ | ❌ | ❌ | ❌ | Not started |
| CTAT | ✅ (OCR) | ❌ | N/A | N/A | ❌ | Needs integration |

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
