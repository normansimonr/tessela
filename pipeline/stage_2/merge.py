#!/usr/bin/env python3
"""
Stage 2: Merge pre-computed normalizations into aligned database.

This script integrates semantic normalizations from CSV files into the
tessela_2_normalised.db database, matching verses across different
coordinate systems and generating comprehensive validation reports.
"""

import sqlite3
import csv
import json
import re
import sys
from pathlib import Path
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass, asdict
from collections import defaultdict

# Map CSV book names to database codes
# Covers: English names, Latin names, code variants, LXX variants
BOOK_NAME_MAP = {
    # English standard
    "Genesis": "GEN",
    "Exodus": "EXO",
    "Leviticus": "LEV",
    "Numbers": "NUM",
    "Deuteronomy": "DEU",
    "Joshua": "JOS",
    "Judges": "JDG",
    "Ruth": "RUT",
    "1 Samuel": "1SA",
    "2 Samuel": "2SA",
    "1 Kings": "1KI",
    "2 Kings": "2KI",
    "1 Chronicles": "1CH",
    "2 Chronicles": "2CH",
    "Ezra": "EZR",
    "Nehemiah": "NEH",
    "Esther": "EST",
    "Job": "JOB",
    "Psalms": "PSA",
    "Proverbs": "PRO",
    "Ecclesiastes": "ECC",
    "Isaiah": "ISA",
    "Jeremiah": "JER",
    "Lamentations": "LAM",
    "Ezekiel": "EZK",
    "Daniel": "DAN",
    "Hosea": "HOS",
    "Joel": "JOL",
    "Amos": "AMO",
    "Obadiah": "OBA",
    "Jonah": "JON",
    "Micah": "MIC",
    "Nahum": "NAM",
    "Habakkuk": "HAB",
    "Zephaniah": "ZEP",
    "Haggai": "HAG",
    "Zechariah": "ZEC",
    "Malachi": "MAL",
    "Song of Solomon": "SNG",
    
    # Code variants (some CSVs have codes directly)
    "GEN": "GEN",
    "EXO": "EXO",
    "LEV": "LEV",
    "NUM": "NUM",
    "DEU": "DEU",
    "JOS": "JOS",
    "JDG": "JDG",
    "RUT": "RUT",
    "1SA": "1SA",
    "2SA": "2SA",
    "1KI": "1KI",
    "2KI": "2KI",
    "1CH": "1CH",
    "2CH": "2CH",
    "EZR": "EZR",
    "NEH": "NEH",
    "EST": "EST",
    "JOB": "JOB",
    "PSA": "PSA",
    "PRO": "PRO",
    "ECC": "ECC",
    "ISA": "ISA",
    "JER": "JER",
    "LAM": "LAM",
    "EZK": "EZK",
    "DAN": "DAN",
    "HOS": "HOS",
    "JOL": "JOL",
    "AMO": "AMO",
    "OBA": "OBA",
    "JON": "JON",
    "MIC": "MIC",
    "NAM": "NAM",
    "HAB": "HAB",
    "ZEP": "ZEP",
    "HAG": "HAG",
    "ZEC": "ZEC",
    "MAL": "MAL",
    "SNG": "SNG",
    
    # Latin / LXX variants
    "Josue": "JOS",
    "Joshua (Vaticanus)": "JOS",
    "Judges (Vaticanus)": "JDG",
    "1 Paralipomenon": "1CH",
    "2 Paralipomenon": "2CH",
    "1 Esdras": "EZR",  # Approximation
    "2 Esdras": "NEH",  # Approximation
    "3 Kings": "1KI",
    "4 Kings": "2KI",
    "Osee": "HOS",
    "Jeremias": "JER",
    "Jeremias (Aquila)": "JER",
    "Jeremias (Symmachus)": "JER",
    "Lamentations of Jeremias": "LAM",
    "Ezechiel": "EZK",
    "Daniel (Old Greek)": "DAN",
    "Jonas": "JON",
    "Micheas": "MIC",
    "Habacuc": "HAB",
    "Sophonias": "ZEP",
    "Aggeus": "HAG",
    "Zacharias": "ZEC",
    "Malachias": "MAL",
    "Isaias": "ISA",
    "Abdias": "OBA",
    "Canticle of Canticles": "SNG",
    "Song of Songs": "SNG",
}


@dataclass
class VerseMatch:
    """Result of matching a CSV verse to a database verse."""
    csv_book_name: str
    csv_chapter: str
    csv_verse: str
    csv_text: str
    
    db_verse_id: Optional[str] = None
    db_book: Optional[str] = None
    db_chapter: Optional[str] = None
    db_verse: Optional[str] = None
    db_text: Optional[str] = None
    
    match_status: str = "unmatched"  # matched, unmatched, text_mismatch
    text_match: bool = False
    normalization: Optional[str] = None


def normalize_book_name(csv_name: str) -> Optional[str]:
    """Convert CSV book name to database code."""
    if csv_name in BOOK_NAME_MAP:
        return BOOK_NAME_MAP[csv_name]
    return None


def load_book_mapping(db_path: str) -> Dict[str, str]:
    """Load book code mapping from database."""
    db = sqlite3.connect(db_path)
    cur = db.cursor()
    cur.execute("SELECT code, name FROM book_mapping")
    mapping = {row[1]: row[0] for row in cur.fetchall()}
    db.close()
    return mapping


def build_verse_lookup(db_path: str, tradition: str) -> Dict[Tuple[str, str, str], str]:
    """
    Build lookup table: (book, chapter, verse) → verseID.
    
    Args:
        tradition: 'mt', 'lxx', 'vulgate', etc.
    
    Returns:
        Dict mapping (book_code, chapter, verse_number) to verseID
    """
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    cur = db.cursor()
    
    lookup = {}
    
    if tradition == 'mt':
        # MT uses hebrew_chapter and hebrew_startVerse
        cur.execute("""
            SELECT verseID, book, hebrew_chapter, hebrew_startVerse 
            FROM raw_masoretic
        """)
        for row in cur.fetchall():
            key = (row['book'], row['hebrew_chapter'], row['hebrew_startVerse'])
            lookup[key] = row['verseID']
    
    elif tradition == 'lxx':
        cur.execute("""
            SELECT verseID, book, chapter, startVerse 
            FROM raw_septuagint
        """)
        for row in cur.fetchall():
            key = (row['book'], row['chapter'], row['startVerse'])
            lookup[key] = row['verseID']
    
    elif tradition == 'vulgate':
        cur.execute("""
            SELECT verseID, book, chapter, startVerse 
            FROM raw_vulgate
        """)
        for row in cur.fetchall():
            key = (row['book'], row['chapter'], row['startVerse'])
            lookup[key] = row['verseID']
    
    db.close()
    return lookup


def get_verse_text(db_path: str, tradition: str, verse_id: str) -> Optional[str]:
    """Get the text of a verse from database."""
    db = sqlite3.connect(db_path)
    cur = db.cursor()
    
    if tradition == 'mt':
        cur.execute("SELECT verseText FROM raw_masoretic WHERE verseID = ?", (verse_id,))
    elif tradition == 'lxx':
        cur.execute("SELECT verseText FROM raw_septuagint WHERE verseID = ?", (verse_id,))
    elif tradition == 'vulgate':
        cur.execute("SELECT verseText FROM raw_vulgate WHERE verseID = ?", (verse_id,))
    
    result = cur.fetchone()
    db.close()
    return result[0] if result else None


def normalize_text(text: str) -> str:
    """Normalize text for comparison: strip punctuation, spaces, lowercase."""
    # Remove all punctuation and normalize whitespace
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()


def match_verse(csv_row: dict, tradition: str, db_path: str, 
                verse_lookup: Dict, book_mapping: Dict) -> VerseMatch:
    """Match a CSV verse to a database verse."""
    csv_book_name = csv_row['book_name']
    csv_chapter = csv_row['chapter']
    csv_verse = csv_row['verse'].rstrip('0').rstrip('.') if csv_row['verse'].endswith('.0') else csv_row['verse']
    csv_text = csv_row['text']
    normalization = csv_row['normalization']
    
    # Convert book name
    db_book = normalize_book_name(csv_book_name)
    if not db_book:
        return VerseMatch(
            csv_book_name=csv_book_name,
            csv_chapter=csv_chapter,
            csv_verse=csv_verse,
            csv_text=csv_text,
            match_status="unmatched",
            normalization=normalization
        )
    
    # Look up verse
    lookup_key = (db_book, csv_chapter, csv_verse)
    verse_id = verse_lookup.get(lookup_key)
    
    if not verse_id:
        return VerseMatch(
            csv_book_name=csv_book_name,
            csv_chapter=csv_chapter,
            csv_verse=csv_verse,
            csv_text=csv_text,
            db_book=db_book,
            match_status="unmatched",
            normalization=normalization
        )
    
    # Get DB text
    db_text = get_verse_text(db_path, tradition, verse_id)
    db_book_code, db_chapter, db_verse = db_book, csv_chapter, csv_verse
    
    # Compare texts
    text_match = normalize_text(csv_text) == normalize_text(db_text or "")
    match_status = "matched" if text_match else "text_mismatch"
    
    return VerseMatch(
        csv_book_name=csv_book_name,
        csv_chapter=csv_chapter,
        csv_verse=csv_verse,
        csv_text=csv_text,
        db_verse_id=verse_id,
        db_book=db_book,
        db_chapter=db_chapter,
        db_verse=db_verse,
        db_text=db_text,
        match_status=match_status,
        text_match=text_match,
        normalization=normalization
    )


def process_csv(csv_path: str, tradition: str, db_path: str, 
                verse_lookup: Dict, book_mapping: Dict) -> List[VerseMatch]:
    """Process a CSV file and match all verses."""
    matches = []
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i % 5000 == 0:
                print(f"  Processing row {i}...", file=sys.stderr)
            match = match_verse(row, tradition, db_path, verse_lookup, book_mapping)
            matches.append(match)
    
    return matches


def save_mapping_csv(matches: List[VerseMatch], output_path: str):
    """Save matches to CSV."""
    fieldnames = [
        'csv_book_name', 'csv_chapter', 'csv_verse', 'db_book', 'db_chapter', 
        'db_verse', 'db_verse_id', 'match_status', 'text_match'
    ]
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for match in matches:
            row = {k: getattr(match, k) for k in fieldnames}
            writer.writerow(row)


def print_stats(matches: List[VerseMatch], tradition: str):
    """Print matching statistics."""
    total = len(matches)
    matched = sum(1 for m in matches if m.match_status == "matched")
    text_mismatch = sum(1 for m in matches if m.match_status == "text_mismatch")
    unmatched = sum(1 for m in matches if m.match_status == "unmatched")
    
    match_rate = (matched / total * 100) if total > 0 else 0
    
    print(f"\n{tradition.upper()} Matching Results:")
    print(f"  Total verses: {total}")
    print(f"  Matched (text ok): {matched} ({match_rate:.1f}%)")
    print(f"  Text mismatch: {text_mismatch}")
    print(f"  Unmatched: {unmatched}")


if __name__ == "__main__":
    db_path = "pipeline/stage_2/tessela_2_normalised.db"
    
    # Load mappings
    book_mapping = load_book_mapping(db_path)
    
    print("=" * 70)
    print("STAGE 2: MERGE PRE-COMPUTED NORMALIZATIONS")
    print("=" * 70)
    
    # Process each tradition
    for tradition, csv_file in [
        ('mt', 'pipeline/masoretic_normalised.csv'),
        ('lxx', 'pipeline/septuagint_normalised.csv'),
        ('vulgate', 'pipeline/vulgate_normalised.csv'),
    ]:
        print(f"\n{tradition.upper()}: Building verse lookup...", file=sys.stderr)
        verse_lookup = build_verse_lookup(db_path, tradition)
        
        print(f"{tradition.upper()}: Processing CSV...", file=sys.stderr)
        matches = process_csv(csv_file, tradition, db_path, verse_lookup, book_mapping)
        
        # Save mapping
        output_csv = f"pipeline/stage_2/{tradition}_mapping.csv"
        save_mapping_csv(matches, output_csv)
        print(f"  Saved: {output_csv}")
        
        # Print stats
        print_stats(matches, tradition)

print("\n" + "=" * 70)
print("Phase 1 complete: Coordinate mapping generated")
print("=" * 70)
