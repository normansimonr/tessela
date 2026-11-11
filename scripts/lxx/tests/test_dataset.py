"""Tests for the generated Septuagint dataset."""

import csv
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lxx import align, dataset, tov  # noqa: E402

DATA = Path(__file__).resolve().parents[3] / "data" / "intermediate_datasets" / "septuagint"
RAW = Path(__file__).resolve().parents[3] / "data" / "raw"


def test_checked_in_dataset_passes_the_checks() -> None:
    assert dataset.check_dataset(DATA / "tov_flagged.csv") == []


def test_dataset_has_the_expected_shape() -> None:
    with (DATA / "tov_flagged.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 12951
    assert all(row["book"] and row["chapter"] and row["verse"] for row in rows)
    assert all(row["greek"] or row["masoretic"] for row in rows)
    assert sum(1 for row in rows if row["lxx_only"] == "yes") == 167


@pytest.mark.skipif(
    not (RAW / "LXX_Tov").is_dir(),
    reason="Tov's CATSS .par files are not tracked (licensing); rebuild them locally first",
)
def test_dataset_is_reproduced_from_the_raw_files() -> None:
    rows = dataset.build_dataset(RAW, tov, align)
    expected = (DATA / "tov_flagged.csv").read_text(encoding="utf-8")
    from io import StringIO
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=dataset.COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    assert buffer.getvalue() == expected
