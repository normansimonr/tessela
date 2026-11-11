#!/usr/bin/env python3
"""Print a compact MT / SP / DSS comparison for a reference.

Examples:
    python3 scripts/demo.py "DEU 32:8"
    python3 scripts/demo.py "Genesis 2:2"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.witnesses import diff_segments, readings  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("reference", nargs="?", default="DEU 32:8",
                        help="reference such as 'DEU 32:8' or 'Genesis 2:2'")
    args = parser.parse_args(argv)

    book_id, items = readings(args.reference)
    print(f"{args.reference}  ({book_id})")
    print("=" * 72)
    if not items:
        print("No readings found in the curated datasets.")
        return 1

    for reading in items:
        print(f"{reading.witness:4} {reading.detail}: {reading.text}")

    base = next((reading for reading in items if reading.witness == "MT"), None)
    if base is not None:
        print("\nDifferences vs MT (normalised consonantal comparison):")
        for reading in items:
            if reading is base:
                continue
            changes = diff_segments(base.text, reading.text)
            if not changes:
                print(f"  {reading.witness} {reading.detail}: identical")
            for left, right in changes:
                print(f"  {reading.witness} {reading.detail}: MT {left!r} -> {right!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
