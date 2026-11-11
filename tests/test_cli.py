"""Tests for the ``tessela`` CLI."""

from pathlib import Path

from src.cli import main


def test_dossier_markdown(capsys) -> None:
    assert main(["dossier", "DEU 32:8"]) == 0
    output = capsys.readouterr().out
    assert "# Textual dossier: DEU 32:8" in output
    assert "Leningrad Codex" in output
    assert "## Provenance" in output


def test_dossier_text(capsys) -> None:
    assert main(["dossier", "DEU 32:8", "--format", "text"]) == 0
    output = capsys.readouterr().out
    assert "DEU 32:8" in output
    assert "Differences vs MT" in output


def test_dossier_writes_to_file(tmp_path: Path) -> None:
    output = tmp_path / "dossier.md"
    assert main(["dossier", "GEN 2:2", "--out", str(output)]) == 0
    assert output.read_text(encoding="utf-8").startswith("# Textual dossier: GEN 2:2")


def test_dossier_rejects_unknown_book(capsys) -> None:
    assert main(["dossier", "Nope 1:1"]) == 2
    assert "Unknown book" in capsys.readouterr().err
