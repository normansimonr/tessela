# Requirements: Stage 2 Normalization

## Goal
Semantically normalize (decompose) the aligned biblical texts into atomic propositions using the Gemini 3.1 Flash Lite API.

## Scope
- Process all traditions: MT, LXX, Vulgate, Samaritan, and Qumran.
- Support both bulk processing (Batch API) and targeted processing (Standard API).

## Decisions
- **API Usage:**
    - Use the **Gemini Batch API** for large requests (anything larger than a single chapter).
    - Use the **Standard Gemini API** for small, targeted requests (single chapter or less).
- **CLI Flags:**
    - `--tradition`: Target a specific tradition (mt, lxx, vulgate, qumran, samaritan).
    - `--book`: Target a specific book.
    - `--chapter`: Target a specific chapter.
- **Storage:**
    - Output database: `pipeline/stage_2/tessela_2_normalised.db`.
    - New columns in the master table: `mt_norm`, `lxx_norm`, `vulgate_norm`, `qumran_norm`, `samaritan_norm`.
    - Results are stored as JSON strings representing an array of propositions.
- **Prompt:**
    - Use the existing `prompts/normalization_prompt.txt`.
- **Concurrency:**
    - Standard API calls should be concurrent to improve performance.

## Context
Normalization is the "semantic bridge" phase. By breaking down complex verses into simple statements, we make it possible to compare text across languages and traditions based on their underlying logic rather than just literal word matches.
