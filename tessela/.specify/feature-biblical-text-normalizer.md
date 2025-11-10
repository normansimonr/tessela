# Feature Specification: Biblical Text Normalizer

**Feature Branch**: `[###-feature-biblical-text-normalizer]`  
**Created**: 2025-11-09
**Status**: Draft  
**Input**: User description: "As a biblical scholar, I want to automatically compare English translations of the Masoretic, Septuagint, and Vulgate texts, so that I can quickly identify meaningful textual variants."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate a Normalized Dataset (Priority: P1)

As a biblical scholar, I want to process the source biblical texts and generate a set of normalized CSV files (one for each source), with each file containing the original text alongside its "deep semantic decomposition", so that I have a standardized dataset for future analysis.

**Why this priority**: This creates the foundational data required for any subsequent comparison or analysis. It is the essential first step.

**Independent Test**: Can be fully tested by running the process and checking the output folder for the three correctly formatted CSV files, each with original data and a new 'normalization' column.

**Acceptance Scenarios**:

1. **Given** the source CSV files are in the `data/` directory, **When** I run the normalization process, **Then** the system creates three new CSV files in the `output/` directory: `masoretic_normalised.csv`, `vulgate_normalised.csv`, and `septuagint_normalised.csv`.
2. **Given** the output CSV files are generated, **When** I inspect them, **Then** each file contains the original data from its respective source file plus an additional column containing the semantic decomposition for each verse.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST read three CSV files from the `data/` directory: `masoretic.csv`, `vulgate.csv`, and `septuagint.csv`.
- **FR-002**: System MUST parse the CSV files according to their specific column structures:
    - `masoretic.csv` and `vulgate.csv`: `book_name`, `chapter`, `verse`, `text`.
    - `septuagint.csv`: `book_name`, `chapter`, `verse`, `potential_difference_verse`, `text`.
- **FR-003**: System MUST skip any verse from `septuagint.csv` where the `potential_difference_verse` column has a value of `false`.
- **FR-004**: System MUST perform deep semantic decomposition on the `text` of each processed verse from all three sources, as defined in the examples below. This is the "normalization" step.
    - *Example 1 (Genesis 1:3): "God said, ‘Let there be light,’ and there was light."* -> *["God said a command.", "God commanded that light should exist.", "Light came to exist."]*
    - *Example 2 (Matthew 8:26): "Why are you afraid, O you of little faith?"* -> *["Jesus asked why his disciples were afraid.", "Jesus said that his disciples had little faith."]*
    - *Example 3 (Psalm 8:1): "How majestic is your name in all the earth!"* -> *["The psalmist exclaimed that God’s name is majestic in all the earth."]*
- **FR-005**: System MUST generate three CSV files in a dedicated `output/` folder, named `masoretic_normalised.csv`, `vulgate_normalised.csv`, and `septuagint_normalised.csv`.
- **FR-006**: Each output CSV file MUST contain all the original data from the corresponding source file's processed verses, plus an additional column named `normalization` which contains the array of decomposed propositions for that verse.

### Key Entities *(include if feature involves data)*

- **Verse**: Represents a single biblical verse. Key attributes: `book_name`, `chapter`, `verse`, `text`, `source_translation`.
- **Translation**: Represents a specific version of the text. Key attributes: `name` (e.g., "Masoretic", "Septuagint", "Vulgate").
- **Proposition**: Represents a single, atomic statement decomposed from a verse's text. Key attribute: `statement_text`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The system can process the three source files and generate the three output CSVs in under 5 minutes.
- **SC-002**: The three output CSV files correctly include the `normalization` column populated with the decomposed propositions.
- **SC-003**: The Septuagint filtering is applied correctly, with all verses where `potential_difference_verse` is `false` being excluded from the output.
- **SC-004**: The semantic decomposition model achieves a user-rated accuracy of over 90% on a curated test set of 100 verses.
