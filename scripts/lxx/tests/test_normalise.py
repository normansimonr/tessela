"""Tests for the normalisation reuse."""

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lxx import normalise  # noqa: E402


def test_reuses_a_matching_text_and_leaves_the_rest_missing(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset.csv"
    with dataset.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["jps_ref", "jps", "lxx_ref", "brenton"])
        writer.writeheader()
        writer.writerow({"jps_ref": "GEN 1:1", "jps": "In the beginning.",
                         "lxx_ref": "GEN 1:1", "brenton": "In the beginning."})
        writer.writerow({"jps_ref": "GEN 1:2", "jps": "And the earth was void.",
                         "lxx_ref": "", "brenton": ""})

    out = tmp_path / "normalisation"
    out.mkdir()
    (out / "jps.csv").write_text(
        "ref,text,propositions\n"
        f'GEN 1:1,"In the beginning.","{json.dumps(["God created."]).replace(chr(34), chr(34) * 2)}"\n',
        encoding="utf-8",
    )
    normalise.normalise(dataset, out, provider="none", only="jps")

    rows = list(csv.DictReader((out / "jps.csv").open(newline="", encoding="utf-8")))
    assert [row["ref"] for row in rows] == ["GEN 1:1"]
    assert json.loads(rows[0]["propositions"]) == ["God created."]


def test_missing_list_names_every_uncovered_verse(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset.csv"
    with dataset.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["book", "chapter", "verse",
                                                    "jps_ref", "jps", "lxx_ref",
                                                    "brenton", "lxx_only"])
        writer.writeheader()
        writer.writerow({"book": "GEN", "chapter": 1, "verse": 1,
                         "jps_ref": "GEN 1:1", "jps": "In the beginning.",
                         "lxx_ref": "GEN 1:1", "brenton": "In the beginning.",
                         "lxx_only": "no"})
        writer.writerow({"book": "GEN", "chapter": 1, "verse": 2,
                         "jps_ref": "GEN 1:2", "jps": "And the earth was void.",
                         "lxx_ref": "", "brenton": "", "lxx_only": "no"})

    out = tmp_path / "normalisation"
    out.mkdir()
    (out / "jps.csv").write_text(
        "ref,text,propositions\n"
        f'GEN 1:1,"In the beginning.","{json.dumps(["God created."]).replace(chr(34), chr(34) * 2)}"\n',
        encoding="utf-8",
    )

    rows = normalise.write_missing(dataset, out)
    refs = {(row["translation"], row["ref"]) for row in rows}
    assert refs == {("jps", "GEN 1:2"), ("lxx", "GEN 1:1")}
    written = list(csv.DictReader((out / "missing.csv").open(newline="", encoding="utf-8")))
    assert {(row["translation"], row["ref"]) for row in written} == refs
