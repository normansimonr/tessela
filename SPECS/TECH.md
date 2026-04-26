# Technical Specification

## Stack
- **Language:** Python 3.11+
- **AI Engine:** Google Gemini 3.1 Flash Lite (via `google-generativeai`)
- **Storage:** SQLite 3
- **Data Processing:** Pandas, SQL
- **OCR/Document Processing:** PyMuPDF (fitz), Pillow, pytesseract (for CTAT datasets)

## Architecture: Pipeline-Driven
The repository is organized into a linear sequence of stage-specific folders within the `pipeline/` directory.

### Structure
- `pipeline/original_data/`: Contains all raw CSVs, SQL dumps, and pre-processing scripts (e.g., Tov's LXX processing).
- `pipeline/stage_N/`: Each stage (N=0, 1, 2...) has its own directory.
    - `run.py`: The script that executes the stage's logic.
    - `tessela_N_XXX.db`: The output database for that stage.

### Stage Contract
1.  **Input:** A stage reads its input from the database file located in the *previous* stage's folder (`pipeline/stage_N-1/`). Stage 0 reads from `pipeline/original_data/`.
2.  **Process:** Logic is contained within `pipeline/stage_N/run.py`.
3.  **Output:** A new SQLite database is saved directly within the current stage's folder (`pipeline/stage_N/`).

This structure ensures that each stage is an isolated, reproducible snapshot of the data's evolution.

## Dependency Management
- `pip install -r requirements.txt`
- `GOOGLE_API_KEY` environment variable for AI services.

## Performance
- Concurrent API calls are used to mitigate latency (`ThreadPoolExecutor`).
- Exponential backoff for API rate-limit resilience.
