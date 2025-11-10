# Biblical Text Normalizer

This tool performs deep semantic decomposition on biblical texts from different ancient versions (Masoretic, Septuagint, and Vulgate). It reads verses from CSV files, uses the Google Gemini 2.5 Pro model to normalize them into atomic propositions, and saves the output to new CSV files.

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
├── Dockerfile            # For containerizing the application
└── requirements.txt      # Python dependencies
```

## Prerequisites

- Docker installed and running.
- A Google AI API key with access to the Gemini 2.5 Pro model.

## How to Run

### 1. Prepare Input Data

Place your source CSV files (`masoretic.csv`, `vulgate.csv`, `septuagint.csv`) into the `data/` directory. The files must have the following columns:
- **masoretic.csv / vulgate.csv**: `book_name`, `chapter`, `verse`, `text`
- **septuagint.csv**: `book_name`, `chapter`, `verse`, `potential_difference_verse`, `text`

### 2. Set Up API Key

You must provide your Google AI API key as an environment variable named `GOOGLE_API_KEY`.

### 3. Build the Docker Image

Open a terminal in the project root directory (`tessela/`) and run the following command to build the Docker image:

```bash
docker build -t biblical-normalizer .
```

### 4. Run the Normalization Process

Run the Docker container with the following command. This command does three important things:
1.  Passes your `GOOGLE_API_KEY` into the container.
2.  Mounts your local `data` directory to the container's `/app/data` directory (read-only).
3.  Mounts your local `output` directory to the container's `/app/output` directory so the results are saved to your machine.

```bash
docker run --rm \
  -e GOOGLE_API_KEY="YOUR_API_KEY_HERE" \
  -v "$(pwd)/data":/app/data:ro \
  -v "$(pwd)/output":/app/output \
  biblical-normalizer
```

Replace `"YOUR_API_KEY_HERE"` with your actual Google AI API key.

The process will start, and you will see progress bars for each source file. Once finished, the normalized files (`masoretic_normalised.csv`, etc.) will be available in your `output/` directory.
