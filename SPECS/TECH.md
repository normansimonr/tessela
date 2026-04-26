# Technical Specification

## Stack
- **Language:** Python 3.11+
- **AI Engine:** Google Gemini 3.1 Flash Lite (via `google-generativeai`)
- **Storage:** SQLite 3
- **Data Processing:** Pandas, SQL
- **OCR/Document Processing:** PyMuPDF (fitz), Pillow, pytesseract (for CTAT datasets)

## Architecture: Pipeline-Driven
The repository is transitioning to a linear, stage-gated pipeline. Each stage is defined by:
1.  **Input:** A specific SQLite database file from the *previous* stage + optional raw assets.
2.  **Process:** A set of Python scripts or SQL migrations.
3.  **Output:** A *new* SQLite database file representing the state of the data after that stage.

## Dependency Management
- `pip install -r requirements.txt`
- `GOOGLE_API_KEY` environment variable for AI services.

## Performance
- Concurrent API calls are used to mitigate latency (`ThreadPoolExecutor`).
- Exponential backoff for API rate-limit resilience.
