#!/usr/bin/env python3
"""Fetch or rebuild the non-commercial datasets into ``data/derived/``.

The repository tracks only the curated **reference lists** for the Samaritan
Pentateuch and the Dead Sea Scrolls. Their Hebrew text, and the Tov Septuagint
corpus, are not tracked for licensing reasons (see ``DATA_LICENSES.md``). This
script fetches/rebuilds them locally:

* ``samaritan``  — download the STEPBible SP SWORD module and add the Hebrew text
* ``dss``        — clone the ETCBC/dss dataset and add the DSS readings
* ``septuagint`` — rebuild the Tov corpus from local CATSS ``.par`` files
* ``all``        — run all three (the DSS clone is large, ~2.5 GB)

Outputs (git-ignored):

    data/derived/samaritan.csv
    data/derived/qumran.csv
    data/derived/septuagint/tov_flagged.csv

Usage:
    python3 scripts/fetch_data.py all
    python3 scripts/fetch_data.py dss --dss-dir /path/to/ETCBC-dss
    python3 scripts/fetch_data.py samaritan
    python3 scripts/fetch_data.py septuagint
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DERIVED = DATA / "derived"

TRACKED_SP = DATA / "manual_datasets" / "samaritan" / "samaritan.csv"
TRACKED_DSS = DATA / "manual_datasets" / "qumran" / "qumran.csv"
DERIVED_SP = DERIVED / "samaritan.csv"
DERIVED_DSS = DERIVED / "qumran.csv"
DERIVED_LXX = DERIVED / "septuagint" / "tov_flagged.csv"
DSS_URL = "https://github.com/ETCBC/dss.git"
DEFAULT_DSS_DIR = DATA / "raw" / "dss"


def run(command: list[str]) -> None:
    print(f"$ {' '.join(command)}")
    subprocess.run(command, check=True, cwd=ROOT)


def seed(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def fetch_samaritan() -> None:
    seed(TRACKED_SP, DERIVED_SP)
    run([
        sys.executable,
        str(ROOT / "scripts" / "fetch_samaritan_sp.py"),
        "--csv",
        str(DERIVED_SP),
    ])


def fetch_dss(dss_dir: Path) -> None:
    if not (dss_dir / "tf").is_dir():
        print(f"ETCBC/dss not found at {dss_dir}; cloning (~2.5 GB, shallow)...")
        dss_dir.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", "--depth", "1", DSS_URL, str(dss_dir)])
    seed(TRACKED_DSS, DERIVED_DSS)
    run([
        sys.executable,
        str(ROOT / "scripts" / "fetch_qumran_dss.py"),
        "--dss-dir",
        str(dss_dir),
        "--csv",
        str(DERIVED_DSS),
    ])


def fetch_septuagint() -> None:
    par_dir = DATA / "raw" / "LXX_Tov"
    if not any(par_dir.glob("*.par")):
        raise SystemExit(
            f"Tov's CATSS .par files are missing from {par_dir}.\n"
            "They are not in the public domain and are not tracked; place them "
            "there, then re-run this command."
        )
    DERIVED_LXX.parent.mkdir(parents=True, exist_ok=True)
    run([
        str(ROOT / "scripts" / "lxx-refs"),
        "build",
        "--out",
        str(DERIVED_LXX),
    ])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "command",
        choices=["samaritan", "dss", "septuagint", "all"],
        help="which dataset(s) to fetch or rebuild",
    )
    parser.add_argument(
        "--dss-dir",
        type=Path,
        default=DEFAULT_DSS_DIR,
        help=f"local ETCBC/dss clone (default: {DEFAULT_DSS_DIR})",
    )
    args = parser.parse_args(argv)

    if args.command in ("samaritan", "all"):
        fetch_samaritan()
    if args.command in ("septuagint", "all"):
        fetch_septuagint()
    if args.command in ("dss", "all"):
        fetch_dss(args.dss_dir)

    print("\nDone. Derived datasets are under data/derived/ (git-ignored).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
