# Implementation Plan: Graphical Verse Normalizer

**Branch**: `001-graphical-verse-normalizer` | **Date**: 2025-11-10 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-graphical-verse-normalizer/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature will create a graphical interface for normalizing biblical verses. Users will select a verse from a dropdown menu, and the system will display the normalized text from three datasets: Masoretic, Vulgate, and Septuagint. The application will be deployed as a **single Cloud Run service**, integrating both the FastAPI backend and the Streamlit frontend within a unified Docker container. The implementation will focus on building the core normalization logic in the backend and then integrating it with the frontend for a seamless user experience.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**:
-   **Backend**: FastAPI, Pandas, `google-generativeai`
-   **Frontend**: Streamlit, Requests
**Storage**: Filesystem (for CSV datasets)
**Testing**: pytest
**Target Platform**: Single Docker container running on Cloud Run, hosting both backend and frontend.
**Project Type**: Web application
**Performance Goals**: Normalize and display verses in under 2 seconds.
**Constraints**: The system must be able to handle variations in book names across the different datasets.
**Scale/Scope**: The initial version will support the three provided datasets.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

-   **I. Technology Stack**:
    -   [X] **Containerization**: Docker will be used.
    -   [X] **Programming Language**: Python will be used.
    -   [X] **AI/NLP Engine**: The `google-generativeai` library will be used for normalization.

All constitution gates pass.

## Project Structure

### Documentation (this feature)

```text
specs/001-graphical-verse-normalizer/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
.
├── Dockerfile           # Unified Dockerfile for Cloud Run deployment
├── run.sh               # Entrypoint script for the Docker container
├── backend/
│   └── src/
│       ├── models/
│       ├── services/
│       └── api/
└── frontend/
    └── src/
        ├── components/
        ├── pages/
        └── services/
```

**Structure Decision**: The project will maintain separate `backend` and `frontend` directories for development clarity. However, for Cloud Run deployment, a unified `Dockerfile` and `run.sh` script at the project root will combine both into a single container.

## Deployment Strategy for Cloud Run

To meet the requirement of a single application runnable on Cloud Run, the backend (FastAPI) and frontend (Streamlit) will be co-located within a single Docker container.

1.  **Unified `Dockerfile`**: A `Dockerfile` will be created at the project root. This Dockerfile will:
    *   Install all Python dependencies for both backend and frontend.
    *   Copy all necessary source code from `backend/` and `frontend/`.
    *   Set up the environment for both services.
2.  **Entrypoint Script (`run.sh`)**: An executable shell script (`run.sh`) will be the `CMD` for the Docker container. This script will:
    *   Start the FastAPI application in the background on a designated internal port (e.g., `8001`).
    *   Start the Streamlit application, ensuring it binds to the `PORT` environment variable provided by Cloud Run (typically `8080`). Streamlit will be the primary HTTP server exposed by the container.
3.  **Internal Communication**: The Streamlit frontend (`frontend/src/app.py`) will be modified to direct its API calls to the FastAPI backend using `http://localhost:8001`, facilitating internal communication within the container.
4.  **Removal of `backend/Dockerfile`**: The `backend/Dockerfile` will be removed as its functionality will be superseded by the unified root `Dockerfile`.

## Feature Implementation Details

### FR-010: Deep Semantic Decomposition

**Objective**: Implement the deep semantic decomposition of biblical text as specified in FR-010, utilizing the `google-generativeai` library.

**Changes to `backend/src/normalization_service.py`**:
- The `NormalizationService` class will be modified.
- The existing `normalize_text` method will be renamed to `decompose_text`.
- A new private method `_load_normalization_prompt` will be added to load the detailed prompt from `prompts/normalization_prompt.txt`.
- The `decompose_text` method will use this loaded prompt, injecting the input `verse_text`.
- The method will be updated to parse the generative AI's response as a JSON array of strings, as required by FR-010.
- Necessary imports for `json` and `List` from `typing` will be added.
- The path to `prompts/normalization_prompt.txt` will be resolved relative to the project root to ensure robustness.

**Changes to `backend/src/api/main.py`**:
- The `/normalize` endpoint (or a new `/decompose` endpoint, to be decided during implementation) will be updated to instantiate `NormalizationService` and call the new `decompose_text` method.
- The endpoint will handle the `List[str]` output from `decompose_text` and return it appropriately in the API response.

**Changes to `backend/tests/test_normalization_service.py`**:
- A new test case will be added to `test_normalization_service.py` to specifically verify the functionality of `decompose_text`.
- This test will mock the `google.generativeai` response to ensure the JSON parsing and the semantic decomposition logic work as expected, using the examples provided in FR-010.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
| :--- | :--- | :--- |
| N/A | | |