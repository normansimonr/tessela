"""Tests for the Gemini-backed normalization service, using a fake model."""

from pathlib import Path

import pytest

from src import normalization_service


class FakeResponse:
    def __init__(self, text: str) -> None:
        self.text = text


class FakeModel:
    def __init__(self, text: str) -> None:
        self.text = text
        self.prompts: list[str] = []

    def generate_content(self, prompt: str) -> FakeResponse:
        self.prompts.append(prompt)
        return FakeResponse(self.text)


def _prompt(tmp_path: Path, body: str = "Verse: {verse_text}") -> str:
    path = tmp_path / "prompt.txt"
    path.write_text(body, encoding="utf-8")
    return str(path)


def test_normalize_text_parses_json(tmp_path: Path) -> None:
    model = FakeModel('```json\n["a", "b"]\n```')
    result = normalization_service.normalize_text(
        "GEN", 1, 1, "In the beginning", _prompt(tmp_path), model=model
    )
    assert result == ["a", "b"]
    assert model.prompts == ["Verse: In the beginning"]


def test_normalize_text_returns_empty_for_empty_input(tmp_path: Path) -> None:
    model = FakeModel("[]")
    assert (
        normalization_service.normalize_text(
            "GEN", 1, 1, "nan", _prompt(tmp_path), model=model
        )
        == []
    )
    assert model.prompts == []


def test_normalize_text_rejects_non_list_output(tmp_path: Path) -> None:
    model = FakeModel('"not a list"')
    with pytest.raises(ValueError, match="list of strings"):
        normalization_service.normalize_text(
            "GEN", 1, 1, "text", _prompt(tmp_path), model=model
        )


def test_compare_verses_parses_result(tmp_path: Path) -> None:
    model = FakeModel('[true, "a difference"]')
    result = normalization_service.compare_verses(
        '["a"]', '["b"]', _prompt(tmp_path, "Compare"), model=model
    )
    assert result == [True, "a difference"]


def test_compare_verses_skips_empty_input() -> None:
    assert normalization_service.compare_verses("", "[]", "unused") == []


def test_compare_verses_rejects_malformed_output(tmp_path: Path) -> None:
    model = FakeModel('{"not": "a pair"}')
    with pytest.raises(ValueError, match="bool, justification"):
        normalization_service.compare_verses(
            '["a"]', '["b"]', _prompt(tmp_path, "Compare"), model=model
        )
