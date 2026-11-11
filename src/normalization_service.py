"""Gemini-backed semantic normalization and comparison services.

The model is configurable through ``GEMINI_MODEL`` (default:
``gemini-3.1-flash-lite``, per ``SPECS/TECH.md``). A model object can be
injected for tests, so the parsing and prompt-building logic can be verified
without a network call.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Protocol

from src.utils import retry_with_exponential_backoff

LOGGER = logging.getLogger(__name__)
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")


class Model(Protocol):
    """The small part of the Gemini model interface used here."""

    def generate_content(self, prompt: str) -> Any: ...


def configure_api_key() -> None:
    """Configure the Google Generative AI client from ``GOOGLE_API_KEY``."""
    import google.generativeai as genai

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set.")
    genai.configure(api_key=api_key)


def get_model(model_name: str | None = None) -> Model:
    """Return a configured Gemini model."""
    import google.generativeai as genai

    configure_api_key()
    return genai.GenerativeModel(model_name=model_name or DEFAULT_MODEL)


def _read_prompt(prompt_path: str) -> str:
    with open(prompt_path, encoding="utf-8") as handle:
        return handle.read()


def _parse_json_response(response: Any) -> Any:
    text = getattr(response, "text", "")
    cleaned = text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned)


@retry_with_exponential_backoff()
def normalize_text(
    book_name: str,
    chapter: int,
    verse: int,
    verse_text: str,
    prompt_path: str,
    model_name: str | None = None,
    model: Model | None = None,
) -> list[str]:
    """Decompose a verse into atomic propositions.

    Returns an empty list for empty input. Invalid model output raises
    ``ValueError``; API errors are left to the caller (after the retry
    decorator has handled rate limits).
    """
    text = str(verse_text).strip()
    if not text or text.lower() == "nan":
        LOGGER.warning("Empty verse for %s %s:%s; skipping", book_name, chapter, verse)
        return []

    prompt = _read_prompt(prompt_path).format(verse_text=text)
    active_model = model or get_model(model_name)
    response = active_model.generate_content(prompt)
    propositions = _parse_json_response(response)

    if not isinstance(propositions, list) or not all(
        isinstance(item, str) for item in propositions
    ):
        raise ValueError(
            "Expected a JSON list of strings from the normalization model, "
            f"got {type(propositions).__name__}"
        )
    return propositions


@retry_with_exponential_backoff()
def compare_verses(
    jps_norm: str,
    lxx_norm: str,
    prompt_path: str,
    model_name: str | None = None,
    model: Model | None = None,
) -> list:
    """Compare two normalized verses and return ``[bool, justification]``."""
    if not jps_norm or not lxx_norm or jps_norm == "[]" or lxx_norm == "[]":
        return []

    prompt = (
        _read_prompt(prompt_path)
        + f"\n\nSource 1: JPS:\n\n{jps_norm}\n\nSource 2: LXX:\n\n{lxx_norm}"
    )
    active_model = model or get_model(model_name)
    response = active_model.generate_content(prompt)
    comparison = _parse_json_response(response)

    if not isinstance(comparison, list) or len(comparison) != 2:
        raise ValueError(
            "Expected [bool, justification] from the comparison model, "
            f"got {comparison!r}"
        )
    return comparison
