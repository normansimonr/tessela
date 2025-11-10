# Implementation Plan: Biblical Text Normalizer

**Branch**: `###-feature-biblical-text-normalizer` | **Date**: 2025-11-09 | **Spec**: [feature-biblical-text-normalizer.md](tessela/.specify/feature-biblical-text-normalizer.md)

## Summary

This plan outlines the steps to create the "Biblical Text Normalizer". The goal is to build a Python application that reads three CSV files containing biblical texts (Masoretic, Vulgate, Septuagint), performs a deep semantic decomposition on each verse using a generative AI model, and outputs three new CSV files containing the original data plus the decomposed propositions. The entire process will be containerized using Docker.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: `pandas`, `google-generativeai`
**AI Model**: Gemini 2.5 Pro
**Storage**: CSV files for input and output.
**Testing**: `pytest`
**Target Platform**: Docker container on a Linux host.
**Project Type**: Single project (batch processing script).
**Constraints**: Must handle API keys securely (via environment variables).

## Constitution Check

The plan adheres to the project constitution:
- **Docker**: A `Dockerfile` will be created to containerize the application.
- **Python**: The entire application will be written in Python.
- **google-generativeai**: This library will be used for the core normalization logic.

## Project Structure

```text
tessela/
├── data/
│   ├── masoretic.csv
│   ├── septuagint.csv
│   └── vulgate.csv
├── output/
│   └── .gitkeep
├── prompts/
│   └── normalization_prompt.txt
├── src/
│   ├── __init__.py
│   ├── data_loader.py
│   └── normalization_service.py
├── tests/
│   ├── __init__.py
│   ├── test_data_loader.py
│   └── test_normalization_service.py
├── scripts/
│   └── run_normalization.py
├── Dockerfile
├── requirements.txt
└── README.md
```

**Structure Decision**: A simple, single-project structure is chosen. It clearly separates the core logic (`src`), the executable script (`scripts`), tests (`tests`), and data (`data`/`output`). This is ideal for a self-contained batch processing tool.

## Implementation Steps

### Phase 1: Project Setup & Data Loading

1.  **Create Project Structure**: Create the directories outlined above (`src`, `tests`, `scripts`, `output`, `prompts`).
2.  **Create Prompt File**: In the `prompts/` directory, create a file named `normalization_prompt.txt`. This file will contain the instructions for the AI model. The initial prompt should be based on the examples in the specification.
3.  **Initialize Python Environment**: Create a `requirements.txt` file and add `pandas` and `google-generativeai`.
4.  **Implement Data Loader**: In `src/data_loader.py`, create a function that takes a file path and returns a pandas DataFrame. Add error handling for file-not-found scenarios.
5.  **Implement Septuagint Filter**: In `src/data_loader.py`, create a function that takes the Septuagint DataFrame and filters it according to the `potential_difference_verse` column, returning the filtered DataFrame.
6.  **Unit Tests**: In `tests/test_data_loader.py`, write `pytest` tests for the loading and filtering functions.

### Phase 2: Normalization Service

1.  **Implement Normalization Service**: In `src/normalization_service.py`, create a class or function that:
    - Initializes the `google-generativeai` client using the "Gemini 2.5 Pro" model. **Note**: The API key must be loaded securely from an environment variable, not hardcoded.
    - Loads the prompt from `prompts/normalization_prompt.txt`.
    - Contains a method that takes a string of verse text as input.
    - Constructs the final prompt by combining the loaded instructions with the verse text.
    - Sends the request to the API, receives the response, and parses it to extract the list of propositions.
    - Returns the list of propositions.
2.  **Integration Tests**: In `tests/test_normalization_service.py`, write tests for the service. The actual API call should be mocked to avoid making real network requests during testing.

### Phase 3: Main Orchestration & Output

1.  **Create Main Script**: In `scripts/run_normalization.py`, create the main script that:
    - Uses `argparse` to potentially accept input/output directory paths.
    - Calls the `data_loader` to load all three source files.
    - Applies the Septuagint filter.
    - Iterates through each DataFrame, row by row.
    - For each row, calls the `normalization_service` with the verse text.
    - Stores the returned list of propositions in a new `normalization` column.
    - Saves the three modified DataFrames to their respective new CSV files in the `output/` directory.
2.  **Add Progress Indicators**: Include `print` statements or use a library like `tqdm` to show progress, as processing many verses could take time.

### Phase 4: Containerization & Documentation

1.  **Create Dockerfile**: Write a `Dockerfile` that:
    - Starts from a Python 3.11 base image.
    - Copies the project files into the container.
    - Installs the dependencies from `requirements.txt`.
    - Sets up the environment variable for the API key (e.g., using `ENV` or expecting it to be passed at runtime).
    - Defines the command to run the main script (`scripts/run_normalization.py`).
2.  **Update README**: Update the main `README.md` with:
    - A description of the "Biblical Text Normalizer".
    - Instructions on how to build the Docker image.
    - Instructions on how to run the container, including how to pass the API key and mount the `data` and `output` directories.
