"""Tessela command-line interface."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.witnesses import Reading, diff_segments, readings

PROVENANCE = """## Provenance

- **MT:** Leningrad Codex (`data/reference/versification/leningrad_codex.csv`).
- **SP:** STEPBible SP / CrossWire (non-commercial); fetched by `make data-samaritan`.
- **DSS:** ETCBC/dss 2.0.5 (CC BY-NC 4.0); fetched by `make data-dss`.
- The comparison is consonantal: vowel points, cantillation, maqaf and
  punctuation are normalised away. DSS editorial markers are preserved in the
  source `transcription` column.
"""


def _change_text(left: str, right: str) -> str:
    if not left:
        return f"added `{right}`"
    if not right:
        return f"omitted `{left}`"
    return f"MT `{left}` → `{right}`"


def _missing_hint() -> str:
    return (
        "> Samaritan and DSS readings are not available locally. Run `make data` "
        "to fetch them; they are git-ignored for licensing reasons."
    )


def render_markdown(reference: str, book_id: str, items: list[Reading]) -> str:
    lines = [
        f"# Textual dossier: {reference}",
        "",
        f"**Book:** {book_id}",
        "",
        "## Readings",
        "",
    ]
    for reading in items:
        lines += [
            f"### {reading.witness} — {reading.detail}",
            "",
            f"`{reading.text}`",
            "",
        ]

    base = next((reading for reading in items if reading.witness == "MT"), None)
    if base is not None:
        lines += ["## Differences vs MT", ""]
        for reading in items:
            if reading is base:
                continue
            changes = diff_segments(base.text, reading.text)
            if not changes:
                lines.append(
                    f"- **{reading.witness} {reading.detail}:** identical (normalised)"
                )
            for left, right in changes:
                lines.append(
                    f"- **{reading.witness} {reading.detail}:** {_change_text(left, right)}"
                )
        lines.append("")

    if not any(reading.witness in ("SP", "DSS") for reading in items):
        lines += [_missing_hint(), ""]

    lines.append(PROVENANCE)
    return "\n".join(lines)


def render_text(reference: str, book_id: str, items: list[Reading]) -> str:
    lines = [f"{reference}  ({book_id})", "=" * 72]
    for reading in items:
        lines.append(f"{reading.witness:4} {reading.detail}: {reading.text}")

    base = next((reading for reading in items if reading.witness == "MT"), None)
    if base is not None:
        lines.append("")
        lines.append("Differences vs MT (normalised consonantal comparison):")
        for reading in items:
            if reading is base:
                continue
            changes = diff_segments(base.text, reading.text)
            if not changes:
                lines.append(f"  {reading.witness} {reading.detail}: identical")
            for left, right in changes:
                lines.append(
                    f"  {reading.witness} {reading.detail}: {_change_text(left, right)}"
                )

    if not any(reading.witness in ("SP", "DSS") for reading in items):
        lines += ["", _missing_hint()]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tessela",
        description="Research assistant for Old Testament textual criticism.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    dossier = subparsers.add_parser(
        "dossier", help="render a comparison dossier for a verse"
    )
    dossier.add_argument("reference", help="e.g. 'DEU 32:8' or 'Genesis 2:2'")
    dossier.add_argument(
        "--format",
        choices=["markdown", "text"],
        default="markdown",
        help="output format (default: markdown)",
    )
    dossier.add_argument(
        "--out", type=Path, help="write to a file instead of standard output"
    )

    args = parser.parse_args(argv)

    try:
        book_id, items = readings(args.reference)
    except ValueError as error:
        print(f"tessela: {error}", file=sys.stderr)
        return 2

    if not items:
        print(f"tessela: no readings found for {args.reference}", file=sys.stderr)
        return 1

    if args.format == "markdown":
        rendered = render_markdown(args.reference, book_id, items)
    else:
        rendered = render_text(args.reference, book_id, items)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered + "\n", encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
