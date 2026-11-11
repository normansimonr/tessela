"""The CTAT OCR pipeline: PDFs in, cleaned references out.

Stage 1 — download (download)
  Read urls.csv and fetch the five CTAT volume PDFs from the ZORA repository
  of the University of Zurich into a cache directory (not tracked).

Stage 2 — headers (extract)
  Render each page at 300 dpi, crop the running-head strip with the
  volume-specific coordinates in header_coordinates.csv (odd and even pages
  have different boxes), and OCR the crop with tesseract. The result is
  ocr_results.csv (volume, page, text, pagina) — one row per page.

Stage 3 — clean (clean)
  The OCR text is not a clean reference: it carries page numbers, witness
  sigla (A-E), French book abbreviations and a string of OCR confusions
  (I S/1$, II R/WS, Ir/Jr, ...). The cleaning stage rewrites the book
  abbreviations, splits multi-reference heads on '/', and melts the two verse
  columns into one row per verse: ocr_clean.csv (volume, pagina, book, value).

The cleaning rules are deliberately kept as a literal table: each one records
an OCR error actually seen in these volumes. Add a rule only with an example.

Stage 4 — references (see refs.py)
  ocr_clean.csv and the HOTTP text are combined into refs.csv.
"""

from __future__ import annotations

import csv
import logging
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data" / "manual_datasets" / "ctat"


def download(urls_csv: Path, out_dir: Path) -> list[Path]:
    """Fetch the volume PDFs listed in urls.csv."""
    import pandas as pd
    import requests

    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for row in pd.read_csv(urls_csv).itertuples(index=False):
        target = out_dir / f"{row.volume}.pdf"
        if target.is_file() and target.stat().st_size:
            logging.info("volume %s already downloaded: %s", row.volume, target)
            written.append(target)
            continue
        logging.info("downloading volume %s from %s", row.volume, row.url)
        response = requests.get(row.url, timeout=120)
        response.raise_for_status()
        target.write_bytes(response.content)
        logging.info("saved %s (%.1f MB)", target, target.stat().st_size / 1e6)
        written.append(target)
    return written


def extract(pdfs_dir: Path, out_csv: Path, coordinates_csv: Path = DATA_DIR / "header_coordinates.csv",
            dpi: int = 300, volumes: list[str] | None = None,
            pages: range | None = None) -> list[dict[str, object]]:
    """Render, crop and OCR the running heads of every page.

    `volumes` and `pages` narrow the run (useful for a quick check); by default
    every page of every volume is processed.
    """
    import io

    import fitz  # PyMuPDF
    import pandas as pd
    import pytesseract
    from PIL import Image

    boxes = {row["volume"]: row for row in csv.DictReader(coordinates_csv.open(newline=""))}
    rows: list[dict[str, object]] = []

    for volume, box in sorted(boxes.items()):
        if volumes and volume not in volumes:
            continue
        pdf = pdfs_dir / f"{volume}.pdf"
        if not pdf.is_file():
            logging.warning("missing PDF: %s", pdf)
            continue

        document = fitz.open(pdf)
        for index in range(document.page_count):
            number = index + 1
            if pages and number not in pages:
                continue
            odd = number % 2 == 1
            # The crop boxes are in pixels at 300 dpi, and so is the render.
            crop = (
                float(box["x0odd" if odd else "x0even"]),
                float(box["y0"]),
                float(box["x1odd" if odd else "x1even"]),
                float(box["y1"]),
            )
            page = document.load_page(index)
            pixmap = page.get_pixmap(dpi=dpi)
            image = Image.open(io.BytesIO(pixmap.tobytes("png")))
            header = image.crop(tuple(int(value) for value in crop))
            text = pytesseract.image_to_string(header).strip()
            rows.append({"volume": volume, "page": f"{number}.png",
                         "text": text, "pagina": number})
        document.close()
        logging.info("volume %s: %d pages", volume, len([r for r in rows if r["volume"] == volume]))

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=["volume", "page", "text", "pagina"]).to_csv(out_csv, index=False)
    logging.info("wrote %d OCR rows to %s", len(rows), out_csv)
    return rows


# The OCR corrections: each pair is (what the OCR produced, what it means).
# Kept as one ordered table so the cleaning reads as a record of the errors.
TEXT_CORRECTIONS = [
    ("‘", ""), (".", ","), ("~", ""), ('"', ""),
    ("Fz", "Ez"), ("Fiz", "Ez"), ("Bz", "Ez"), ("pp", "Ps"),
    ("J ", "Jl"), ("Jt", "Jl"),
    ("Ir ", "Jr "), ("In ", "Jr "), ("Jn ", "Jr "), ("dr ", "Jr "),
    ("Il Ch", "II Ch "), ("I] Ch", "II Ch "), ("1] Ch", "II Ch "),
    ("{1 Ch", "II Ch "), ("11Ch", "II Ch"), ("| Ch", "I Ch"),
    ("I Ch 20,25B", "II Ch 20,25B"),
    ("1$", "I S"), ("1S", "I S"), ("1I S", "II S"), ("11S", "II S"),
    ("11 Ch", "II Ch"), ("1I Ch", "II Ch"),
    ("Jg2,1", "Jg 2,1"), ("Jg5,11", "Jg 5,11"), ("Jg7,3", "Jg 7,3"),
    ("Jg9,31A", "Jg 9,31"),
    ("1$1,24A", "I S 1,24"), ("1$3,13A", "I S 3,13"), ("1$7,2", "I S 7,2"),
    ("1$9,24A", "I S 9,24"), ("1$14,41", "I S 14,41"),
    ("WS ", "II S "), ("Il ", "II "), ("ILS ", "II S "), ("It'S ", "II S "),
    ("11 R", "II R"), ("I] R", "II R"),
    ("Jp ", "Jr "), ("MI ", "Mal "),
]
PARENTHESES = r"\(.*?\)"

FINAL_CORRECTIONS = [
    ("II Ch", "2Ch"), ("I Ch", "1Ch"), ("II R", "2R"), ("I R", "1R"),
    ("II S", "2S"), ("I S", "1S"), (",", ":"),
]


def clean(ocr_csv: Path, out_csv: Path) -> object:
    """Turn the OCR page texts into one row per CTAT verse (ocr_clean.csv)."""
    import pandas as pd

    df = pd.read_csv(ocr_csv)
    df = df.drop_duplicates(subset="text", keep="first")

    text = df["text"]
    for old, new in TEXT_CORRECTIONS:
        text = text.str.replace(old, new, regex=False)
    text = text.str.replace(PARENTHESES, "", regex=True).str.strip()
    df["text"] = text

    for old, new in FINAL_CORRECTIONS:
        df["text"] = df["text"].str.replace(old, new, regex=False)
    df = df.drop_duplicates(subset="text", keep="first")

    split = df["text"].str.split(" ", n=1, expand=True)
    split.columns = ["book", "verses"]
    df = pd.concat([df, split], axis=1)

    df["verses"] = df["verses"].str.replace(r"[A-Za-z]", "", regex=True)
    verses = df["verses"].str.split("/", expand=True)
    verses.columns = ["v1", "v2"]
    df = pd.concat([df, verses], axis=1)

    df = df.drop(columns=["text", "page", "verses"])
    df = df.melt(id_vars=["volume", "pagina", "book"])
    df = df.dropna(subset=["value"]).drop(columns=["variable"])
    df = df.drop_duplicates(subset=["book", "value"], keep="first")

    def strip_hyphen(value: str) -> str:
        return value[:-1].strip() if value.endswith("-") else value.strip()

    def add_obadiah_chapter(row: pd.Series) -> str:
        return f"1:{row['value']}" if row["book"] == "Ab" else str(row["value"])

    df["value"] = df["value"].apply(strip_hyphen)
    df["value"] = df[["book", "value"]].apply(add_obadiah_chapter, axis=1)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    logging.info("wrote %d cleaned rows to %s", len(df), out_csv)
    return df
