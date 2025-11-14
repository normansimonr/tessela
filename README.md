# Biblical Text Normalizer

This tool performs deep semantic decomposition on biblical texts from different ancient versions (Masoretic, Septuagint, and Vulgate). It reads verses from CSV files, uses the Google Gemini Flash model to normalize them into atomic propositions, and saves the output to new CSV files.

## Overview

The main goal of this project is to take biblical verses from different translations and break them down into a structured, "normalized" format. This is achieved by using a powerful AI model to understand the semantic meaning of each verse and represent it as a series of simple, atomic statements.

## Architecture

The project is structured as a Python application. Here's a high-level overview of the key components:

- **`run.sh`**: The main entry point for the application. This script sets up the Python environment and executes the normalization process.
- **`scripts/run_normalization.py`**: The core script that orchestrates the normalization. It loads the data, calls the normalization service for each verse, and saves the results. It's designed to be resumable, so if it's interrupted, it can pick up where it left off.
- **`src/data_loader.py`**: This module is responsible for reading the input CSV files and preparing the data for processing.
- **`src/normalization_service.py`**: This service handles the interaction with the Google Gemini API. It takes a verse of text, sends it to the AI model with a specific prompt, and processes the response.
- **`data/`**: This directory contains the input CSV files.
- **`output/`**: This directory is where the normalized CSV files are saved.
- **`prompts/`**: This directory holds the text-based prompts that are used to instruct the AI model on how to perform the normalization.

## Project Structure

```
tessela/
├── data/                 # Input CSV files (masoretic.csv, etc.)
├── output/               # Output CSV files will be generated here
├── prompts/              # Contains the prompt for the AI model
│   └── normalization_prompt.txt
├── src/                  # Python source code for the application
│   ├── data_loader.py
│   └── normalization_service.py
├── scripts/              # Main executable script
│   └── run_normalization.py
├── tests/                # Unit and integration tests
├── run.sh                # Main execution script
└── requirements.txt      # Python dependencies
```

## Prerequisites

- Python 3.11
- A Google AI API key with access to the Gemini Flash model.

## Setup

1.  **Create a Python virtual environment:**
    ```bash
    python3 -m venv .venv
    ```

2.  **Activate the virtual environment:**
    ```bash
    source .venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Run

1.  **Prepare Input Data**

    Place your source CSV files (`masoretic.csv`, `vulgate.csv`, `septuagint.csv`) into the `data/` directory. The files must have the following columns:
    - **masoretic.csv / vulgate.csv**: `book_name`, `chapter`, `verse`, `text`
    - **septuagint.csv**: `book_name`, `chapter`, `verse`, `potential_difference_verse`, `text`

2.  **Set Up API Key**

    You must provide your Google AI API key as an environment variable named `GOOGLE_API_KEY`. You can set it in your shell like this:
    ```bash
    export GOOGLE_API_KEY="YOUR_API_KEY_HERE"
    ```
    Replace `"YOUR_API_KEY_HERE"` with your actual Google AI API key.

3.  **Run the Normalization Process**

    Execute the `run.sh` script from the project root directory:
    ```bash
    ./run.sh
    ```

    The process will start, and you will see progress bars for each source file. The script will log its progress to `normalization.log`. Once finished, the normalized files (`masoretic_normalised.csv`, etc.) will be available in your `output/` directory.

    
# Data sources

The data sources are:

* LXX: Tov's CATSS project (https://ccat.sas.upenn.edu/rak/catss.html) and Brenton's Septuagint (Vaticanus)
* Masoretic text: JPS 1917
* Vulgate: Douay–Rheims Bible
* Qere-Ketiv: TAHOT dataset from STEP-Bible (https://github.com/STEPBible/STEPBible-Data/tree/master/Translators%20Amalgamated%20OT%2BNT, https://stepbible.github.io/STEPBible-Data/)
