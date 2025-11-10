# Feature Specification: Graphical Verse Normalizer

**Feature Branch**: `001-graphical-verse-normalizer`
**Created**: 2025-11-10
**Status**: Draft
**Input**: User description: "There is only one set of dropdown menus in the graphical interface, not a set of dropdowns for each of the datasets (masoretic.csv, vulgate.csv and septuagint.csv). When the user selects a verse from the dropdown, the system normalises the corresponding verse in each of the three datasets. So, the output is three text boxes, one with the normalisation of the verse in masoretic.csv, one with the normalisation of the verse in vulgate.csv and one with the normalisation of the verse in septuagint.csv."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Verse Normalization (Priority: P1)

As a user, I want to select a biblical verse from a dropdown menu and see the normalized text of that verse from three different datasets (Masoretic, Vulgate, and Septuagint) displayed in separate text boxes.

**Why this priority**: This is the core functionality of the feature.

**Independent Test**: The feature can be tested by selecting a verse and verifying that the three text boxes are populated with the correct normalized text.

**Acceptance Scenarios**:

1.  **Given** the graphical interface is loaded, **When** the user selects a verse from the dropdown, **Then** the system displays three text boxes, each containing the normalized text of the selected verse from the Masoretic, Vulgate, and Septuagint datasets, respectively.
2.  **Given** the user has selected a verse, **When** the user selects a different verse from the dropdown, **Then** the content of the three text boxes is updated to reflect the newly selected verse.

### Edge Cases

-   What happens when a selected verse is not present in one or more of the datasets?
-   How does the system handle empty or malformed rows in the CSV files?
-   What is displayed in the text boxes before the user selects a verse for the first time?

## Requirements *(mandatory)*

### Functional Requirements

-   **FR-001**: The system MUST display a single dropdown menu populated with a list of biblical verses.
-   **FR-002**: The list of verses in the dropdown MUST be the union of all unique verses present across all three datasets.
-   **FR-003**: When a user selects a verse, the system MUST read the corresponding verse from `masoretic.csv`, `vulgate.csv`, and `septuagint.csv`.
-   **FR-004**: The system MUST normalize the text of the selected verse from each of the three datasets.
-   **FR-005**: The system MUST display three distinct output areas (e.g., text boxes), one for each dataset's normalized verse.
-   **FR-006**: Each output area MUST be clearly labeled with the name of its corresponding dataset (Masoretic, Vulgate, Septuagint).
-   **FR-007**: If a verse is not found in a particular dataset, its corresponding output area MUST display a clear message indicating that the verse is not available.
-   **FR-008**: The system MUST reconcile different representations of book names (e.g., 'Genesis', 'GEN', '1 Samuel', '1Samuel') across the datasets to ensure a verse is correctly identified.
-   **FR-009**: The system MUST be deployable as a single container on Cloud Run, integrating both the FastAPI backend and the Streamlit frontend. The Streamlit frontend will serve as the primary HTTP interface, communicating internally with the FastAPI backend.
-   **FR-010**: The `/normalize` endpoint MUST perform deep semantic decomposition on the provided `text` (the "normalization" step).
    - *Example 1 (Genesis 1:3): "God said, ‘Let there be light,’ and there was light."* -> *["God said a command.", "God commanded that light should exist.", "Light came to exist."]*
    - *Example 2 (Matthew 8:26): "Why are you afraid, O you of little faith?"* -> *["Jesus asked why his disciples were afraid.", "Jesus said that his disciples had little faith."]*

### Key Entities *(include if feature involves data)*

-   **Verse**: Represents a single biblical verse, identified by book, chapter, and verse number. It has associated text content from three different sources.
-   **Dataset**: Represents a source of biblical text (e.g., Masoretic, Vulgate, Septuagint).

## Deployment Architecture

The application will be deployed as a single Docker container on Google Cloud Run. This container will host both the FastAPI backend and the Streamlit frontend.

*   **FastAPI Backend**: Will run on an internal port (e.g., `8001`) within the container. It will handle API requests for verse data and normalization.
*   **Streamlit Frontend**: Will run on the port exposed by Cloud Run (specified by the `PORT` environment variable, typically `8080`). It will serve the user interface and make HTTP requests to the FastAPI backend at its internal container address (`http://localhost:8001`).
*   **Entrypoint Script (`run.sh`)**: A shell script will be used as the container's entrypoint. This script will be responsible for:
    1.  Starting the FastAPI application in the background.
    2.  Starting the Streamlit application, ensuring it binds to the `PORT` environment variable.

This architecture ensures that the entire application (backend + frontend) is managed as a single deployable unit on Cloud Run, simplifying deployment and management while maintaining clear separation of concerns between the backend API and the user interface.

## Success Criteria *(mandatory)*

### Measurable Outcomes

-   **SC-001**: When a user selects a verse, the normalized text for all three datasets is displayed in under 2 seconds.
-   **SC-002**: 100% of verse selections result in the correct normalized text being displayed for all available datasets.
-   **SC-003**: The user can successfully view the normalized text for any verse present in the dropdown menu.
