# Implementation Plan: Stage 2 Normalization

## Task Group 1: Environment & Setup
1. Create directory `pipeline/stage_2/`.
2. Initialize `tessela_2_normalised.db` by copying `tessela_1_aligned.db`.
3. Add normalization columns to the master table in `tessela_2_normalised.db`:
    - `mt_norm`, `lxx_norm`, `vulgate_norm`, `qumran_norm`, `samaritan_norm`.

## Task Group 2: Core Normalization Logic
1. Create `pipeline/stage_2/run.py`.
2. Implement **Standard API Path**:
    - Use `ThreadPoolExecutor` for concurrent calls.
    - Implement robust error handling and exponential backoff.
    - Logic to parse the AI response and update the database incrementally.
3. Implement **Batch API Path**:
    - Logic to generate `.jsonl` requests from the database.
    - Logic to upload files, create batch jobs, and poll for completion.
    - Logic to download and integrate results back into the SQLite database.

## Task Group 3: CLI Interface
1. Add `argparse` to `run.py` for targeted normalization.
2. Implement the "Small vs Large" threshold logic:
    - If total verses to normalize <= chapter average (~30), use Standard API.
    - Otherwise, default to Batch API (unless forced by a flag).

## Task Group 4: Verification
1. Run a targeted normalization for Genesis 1 (MT).
2. Verify the JSON structure of the `mt_norm` column.
3. Test the resume capability (not re-normalizing already processed verses).
