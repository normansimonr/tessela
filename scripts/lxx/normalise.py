"""Reuse and extend the semantic normalisations of the English verses.

The expensive LLM step is not part of the build: the normalisations are data.
This module keeps the committed normalisation tables in step with the dataset:
a verse whose text has not changed keeps its propositions; a verse with no
normalisation is reported as missing, and only normalised when the caller asks
for the Gemini provider explicitly.
"""

from __future__ import annotations

import csv
import json
import logging
import re
from pathlib import Path

PROMPT = Path(__file__).resolve().parent / "data" / "normalization_prompt.txt"
COLUMNS = ["ref", "text", "propositions"]


def normalise_text(text: str) -> str:
    text = re.sub(r"[^\w\s]", "", text or "").lower()
    return re.sub(r"\s+", " ", text).strip()


def load_existing(path: Path) -> dict[str, dict[str, str]]:
    if not path.is_file():
        return {}
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["ref"]: row for row in csv.DictReader(handle)}


def collect(dataset_path: Path) -> dict[str, dict[str, str]]:
    """Every unique English verse in the dataset, by translation and reference."""
    return {translation: {ref: entry["text"] for ref, entry in refs.items()}
            for translation, refs in collect_rows(dataset_path).items()}


def collect_rows(dataset_path: Path) -> dict[str, dict[str, dict]]:
    """Every unique English verse, with the dataset rows it serves."""
    collected: dict[str, dict[str, dict]] = {"jps": {}, "lxx": {}}
    with dataset_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            for translation, ref_col, text_col in (
                    ("jps", "jps_ref", "jps"), ("lxx", "lxx_ref", "brenton")):
                ref = row[ref_col]
                text = row[text_col]
                if not ref or not text:
                    continue
                entry = collected[translation].setdefault(
                    ref, {"text": text, "rows": []})
                entry["rows"].append({
                    "ref": f"{row.get('book', '')} {row.get('chapter', '')}:{row.get('verse', '')}".strip(),
                    "lxx_only": row.get("lxx_only", "no"),
                })
    return collected


def call_gemini(text: str) -> list[str]:
    """Normalise one verse with Gemini. Only called with --provider gemini."""
    import os

    import google.generativeai as genai

    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("GOOGLE_API_KEY is not set")
    genai.configure(api_key=key)
    prompt = PROMPT.read_text(encoding="utf-8").format(verse_text=text)
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")
    response = model.generate_content(prompt)
    cleaned = response.text.strip().replace("```json", "").replace("```", "").strip()
    result = json.loads(cleaned)
    return result if isinstance(result, list) else []


def missing_rows(dataset_path: Path, out_dir: Path) -> list[dict[str, str]]:
    """The verses that still need normalising, one row per English verse."""
    collected = collect_rows(dataset_path)
    rows: list[dict[str, str]] = []
    for translation in ("jps", "lxx"):
        existing = load_existing(out_dir / f"{translation}.csv")
        for ref, entry in sorted(collected[translation].items()):
            previous = existing.get(ref)
            if previous and normalise_text(previous.get("text", "")) == normalise_text(entry["text"]):
                continue
            served = "; ".join(sorted({row["ref"] for row in entry["rows"]}))
            only = all(row["lxx_only"] == "yes" for row in entry["rows"])
            rows.append({
                "translation": translation,
                "ref": ref,
                "text": entry["text"],
                "serves": served,
                "lxx_only": "yes" if only else "no",
            })
    return rows


def write_missing(dataset_path: Path, out_dir: Path) -> list[dict[str, str]]:
    rows = missing_rows(dataset_path, out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "missing.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["translation", "ref", "text",
                                                    "serves", "lxx_only"],
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    for translation in ("jps", "lxx"):
        count = sum(1 for row in rows if row["translation"] == translation)
        logging.info("%s: %d verses still to normalise", translation, count)
    logging.info("wrote %d rows to %s", len(rows), path)
    return rows


def normalise(dataset_path: Path, out_dir: Path, provider: str = "none",
              only: str = "both", limit: int | None = None) -> None:
    collected = collect(dataset_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    for translation in ("jps", "lxx"):
        if only not in (translation, "both"):
            continue
        path = out_dir / f"{translation}.csv"
        existing = load_existing(path)
        rows = []
        missing = []
        for ref, text in sorted(collected[translation].items()):
            previous = existing.get(ref)
            if previous and normalise_text(previous.get("text", "")) == normalise_text(text):
                rows.append(previous)
            else:
                missing.append((ref, text))

        logging.info("%s: %d verses, %d reusable, %d missing",
                     translation, len(collected[translation]), len(rows), len(missing))

        if provider == "gemini":
            if limit is not None:
                missing = missing[:limit]
            for ref, text in missing:
                try:
                    propositions = call_gemini(text)
                    rows.append({"ref": ref, "text": text,
                                 "propositions": json.dumps(propositions, ensure_ascii=False)})
                except Exception as error:  # noqa: BLE001 - the caller sees the log
                    logging.error("%s: %s failed: %s", translation, ref, error)

        rows.sort(key=lambda row: row["ref"])
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        logging.info("%s: wrote %d rows to %s", translation, len(rows), path)
