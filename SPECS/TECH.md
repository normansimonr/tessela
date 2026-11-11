# Technical Specification: Tessela

## 1. Mission alignment

This document specifies the technical architecture, stack, and data contracts
for Tessela. It must stay aligned with `SPECS/MISSION.md` (the product
contract) and `SPECS/ROADMAP.md` (delivery plan). Any implementation that
changes shipped reality must update this file.

Tessela is a research and decision-support system for Hebrew Bible textual
criticism. It consolidates readings from multiple witnesses, aligns them,
identifies textually significant variants, retrieves scholarly discussion,
generates and evaluates textual-development hypotheses, runs an AI-assisted
adversarial analysis (Monica / Tomás / Ernesto), and produces research
dossiers — all while preserving provenance, distinguishing attested from
reconstructed readings, and making uncertainty explicit.

## 2. Stack

### 2.1 Core
- **Language:** Python 3.11+
- **AI Engine:** Google Gemini (via `google-generativeai`)
  - Default model: **Gemini 3.1 Flash Lite** (per mission; configurable per task)
  - Heavier reasoning tasks (hypothesis generation, adversarial analysis) may use
    a stronger model where cost/latency allow
- **Storage:** SQLite 3 (stage-gated pipeline databases) + structured CSV/JSON
  intermediates where appropriate
- **Data Processing:** Pandas, SQL
- **OCR/Document Processing:** PyMuPDF (fitz), Pillow, pytesseract (for CTAT datasets)
- **Graph/Modelling:** NetworkX (or equivalent) for textual-development graphs/trees
- **Export:** Markdown / PDF generation for research dossiers

### 2.2 Dependencies
- `pip install -r requirements.txt`
- `GOOGLE_API_KEY` environment variable for AI services.
- `sqlite3` CLI for database construction scripts.

### 2.3 Performance
- Concurrent API calls are used to mitigate latency (`ThreadPoolExecutor`).
- Exponential backoff for API rate-limit resilience.
- Long-running AI tasks (hypothesis generation, adversarial analysis) should be
  resumable and checkpointed.

## 3. Architecture: Pipeline-Driven

The repository follows a linear, stage-gated pipeline. Each stage is defined by:

1. **Input:** A specific SQLite database file from the *previous* stage + optional
   raw assets.
2. **Process:** A set of Python scripts or SQL migrations.
3. **Output:** A *new* SQLite database file representing the state of the data
   after that stage.

### 3.1 Stage definitions

| Stage | Name | Input | Output | Purpose |
|---|---|---|---|---|
| 0 | Ingestion | Raw CSVs/SQLs from `data/raw` + manual datasets + CTAT OCR | `tessela_0_raw.db` | Consolidate all witness data into a unified, source-aware schema |
| 1 | Alignment | `tessela_0_raw.db` + mapping scripts | `tessela_1_aligned.db` | Align readings across witnesses; record alignment uncertainty |
| 2 | Normalization | `tessela_1_aligned.db` + Gemini API | `tessela_2_normalised.db` | Atomic semantic propositions per reading |
| 3 | Comparison | `tessela_2_normalised.db` + Gemini API | `tessela_3_compared.db` | Semantic differences flagged with significance classification |
| 4 | Scholarly retrieval | `tessela_3_compared.db` + CTAT PDFs + paper sources | `tessela_4_sourced.db` | Attach CTAT discussion and open-access paper references |
| 5 | Hypothesis generation | `tessela_4_sourced.db` | `tessela_5_hypotheses.db` | Textual-development models (graphs/trees) with probabilities |
| 6 | Adversarial analysis | `tessela_5_hypotheses.db` + Gemini API | `tessela_6_assessed.db` | Monica / Tomás / Ernesto assessments |
| 7 | Dossier export | `tessela_6_assessed.db` | Research dossiers (Markdown/PDF) | Per-variant research reports |

### 3.2 Stage modularity

- Each stage must be independently re-runnable from its input DB.
- A CLI tool (Phase 3) will allow jumping into any stage.
- Stage outputs are immutable artifacts; downstream stages never mutate upstream DBs.

## 4. Data model and provenance (critical)

### 4.1 Reading provenance

Every reading, reconstruction, alignment, and scholarly claim must carry:

- **Source:** where it came from (manuscript edition, translation, retroversion
  author, OCR pipeline, etc.)
- **Witness type:** Masoretic, Qere, Ketiv, Samaritan Pentateuch, Dead Sea
  Scrolls, Septuagint, Vulgate, Peshitta, or scholarly reconstruction
- **Evidence kind:** `attested` (directly in a manuscript/translation),
  `reconstructed` (proposed retroversion), or `secondary_description`
  (English description only, no underlying text)
- **Language:** Hebrew, Greek, Latin, Syriac, or English (for descriptions)
- **Provenance chain:** for reconstructions, the full chain (e.g. Greek wording →
  proposed Hebrew Vorlage → reasoning → uncertainty → alternative explanations)
- **Uncertainty:** explicit confidence level or uncertainty note where applicable
- **Missing data:** explicitly marked as missing (never silently filled)

### 4.2 Variant record

Each significant variant record must include at minimum:

- Biblical location (book, chapter, verse, textual location)
- Base-text reading (Masoretic Text)
- Qere and Ketiv readings (where applicable)
- Readings/descriptions from other witnesses
- Evidence kind for each reading (attested / reconstructed / secondary)
- Language and textual tradition per witness
- Morphological parsing and lexical roots (where available)
- Source references (manuscript, edition, page)
- Scholarly discussion references (CTAT volume/page, paper citations)
- Alignment information and alignment uncertainty
- Semantic assessment (formal / semantic / interpretive significance)
- Hypothesis references (textual-development models)

### 4.3 Attested vs. reconstructed distinction

A reading directly attested in a Hebrew manuscript is **not** the same kind of
evidence as a Hebrew retroversion proposed from a Greek/Latin/Syriac translation.
This distinction must be preserved in storage, analysis, visualization, and
reporting. Retroversions must be labeled as reconstructions and must never be
confused with attested readings.

### 4.4 Missing data policy

Missing information must remain explicitly missing. The system must not silently
fill gaps by guessing. Where data is unavailable (e.g. SP/DSS Hebrew text not
yet transcribed), the record must say so.

## 5. Witness-specific requirements

### 5.1 Masoretic Text
- Principal base text. Hebrew text with morphology and lexical roots where
  available.
- Qere and Ketiv represented explicitly (not flattened).

### 5.2 Samaritan Pentateuch
- Curated set (~20 variants initially). Current data is English-only verse
  references.
- Preserve the distinction: English description ≠ directly transcribed Hebrew.
- Enrich with Hebrew readings and precise source references where possible.

### 5.3 Dead Sea Scrolls
- Curated set (~150 variants). Current data identifies verses and variants in
  English only.
- Record nature and limitations of available evidence. Do not imply Hebrew was
  directly inspected when only English descriptions exist.

### 5.4 Septuagint
- Use Tov's proposed Hebrew retroversions where he argues the Greek reflects a
  Vorlage differing from MT.
- Treat retroversions as **reconstructed** Hebrew readings, not attested.
- Preserve the chain: Greek wording (attested) → proposed Hebrew Vorlage
  (reconstructed) → reasoning → uncertainty → alternatives.

### 5.5 Vulgate
- Additional witness for completeness and corroboration.
- Hebrew retroversion (if investigated) labeled as reconstruction.

### 5.6 Peshitta
- Additional witness. Hebrew retroversion (if investigated) labeled as
  reconstruction.

### 5.7 CTAT (Barthélemy)
- PDFs with index mapping variants to pages. Use as scholarly evidence to
  consult and cite, not as opaque authority.
- Preserve bibliographic details and page-level references.

### 5.8 Open-access papers
- Retrieve and link to specific variants. Extract arguments with precise
  citations. Respect copyright/licensing.

## 6. Semantic evaluation

For each candidate variant, assess whether competing readings differ in meaning
and whether that difference matters for translation. Consider:

- Lexical meaning
- Morphology and syntax
- Grammatical person, number, gender, tense, aspect, verbal stem
- Clause structure and word relationships
- Immediate literary context
- Broader literary and canonical context
- Idiom and usage elsewhere in the Hebrew Bible
- Translation technique in ancient versions
- Interpretive or theological implications

The system must distinguish at least three levels:

1. **Formal difference:** wording, spelling, morphology, or other textual feature
   differs.
2. **Semantic difference:** readings may communicate different meanings.
3. **Interpretive/translational significance:** the difference may affect how the
   passage should be understood or translated.

Preserve reasoning — do not reduce to a binary label without explanation.
Retain potentially relevant formal differences even when judged non-meaningful
(for auditability).

## 7. Scholarly source retrieval

- For each variant, retrieve relevant CTAT discussion and open-access papers.
- Extract specific arguments, cited evidence, and conclusions.
- Preserve exact bibliographic and page references.
- Distinguish direct quotations, paraphrases, and system's own conclusions.
- Represent scholarly disagreement rather than prematurely resolving it.

## 8. Textual development hypotheses (Mission §6)

- Represent as directed graphs or trees: nodes = readings/textual states; edges =
  proposed changes with mechanism, probability, supporting/challenging evidence.
- Alternative models for competing explanations.
- Encode scribal/translational tendencies as explicit analytical considerations
  (visual confusion, omissions/additions, harmonization, grammatical
  normalization, clarification, translation changes, retroversion uncertainty)
  — not as universal laws.
- Assign comparative scores/probabilities based on explicit criteria; do not
  create false impression of mathematical certainty.
- Treat witnesses critically: account for age, character, textual affiliation,
  dependencies, shared ancestry.

## 9. AI-assisted adversarial analysis (Mission §7)

Three principal agents with access to the same underlying evidence:

- **Mónica** — strongest evidence-based case *for* the Masoretic Text reading.
- **Tomás** — strongest evidence-based case *against* the Masoretic Text
  reading (when competing readings exist).
- **Ernesto** — adjudicator: evaluates competing cases, identifies unsupported
  claims/omissions, compares explanatory strength, provides calibrated
  conclusion.

All agents must ground factual claims in the dataset or retrievable sources,
cite specific readings/passages/references, and never invent manuscript
readings, bibliographic references, scholarly positions, or historical
explanations. AI-generated claims must be distinguishable from
source-supported claims.

## 10. Research dossier output (Mission §10)

Per significant variant, produce a research dossier containing:

- Textual location
- MT, Qere, Ketiv readings (as applicable)
- Readings/descriptions from each other witness
- Attested vs. reconstructed distinction
- Original-language evidence and missing data
- Alignment notes and uncertainty
- Semantic assessment
- CTAT discussion and other scholarly sources
- Competing textual-development hypotheses (preferably graphical)
- Proposed changes and rationale per edge
- Evidence supporting/challenging each hypothesis
- Monica's and Tomás's arguments
- Ernesto's assessment and supporting reasons
- Overall confidence, limitations, unresolved questions

Output formats: structured data (SQLite/JSON) + human-readable (Markdown/PDF).

## 11. Principles and methodological safeguards (Mission §8)

- Evidence before conclusions.
- Preserve attested vs. reconstructed distinction throughout.
- Preserve provenance and traceability.
- Make uncertainty explicit.
- Treat witnesses critically (date, character, dependencies).
- Distinguish textual evidence from interpretation.
- Avoid predetermined outcomes (MT neither privileged nor rejected by default).
- Be reproducible and inspectable (deterministic, documented; record inputs,
  outputs, model, config for AI steps).
- Keep the translator/researcher in control.

## 12. Coding conventions

- Follow the pipeline architecture; each stage reads from the previous stage's
  DB and writes a new DB.
- Use structured logging (not `print()`).
- Fail loudly for non-critical work; degrade gracefully on the user-facing path
  with loud logging.
- Prefer schemas/structured data over regex heuristics.
- Treat all external inputs (CSV rows, OCR output, API responses, file paths) as
  untrusted; validate at boundaries.
- Do not commit secrets; use `GOOGLE_API_KEY` env var.

## 13. README policy

`README.md` must reflect developer-facing behaviour: setup, run commands,
environment variables, and project structure. Update it whenever implementation
changes shipped reality.
