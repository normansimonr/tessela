import json
import os

import google.generativeai as genai

from src.utils import retry_with_exponential_backoff


def configure_api_key():
    """
    Configures the Google Generative AI API key from an environment variable.

    Raises:
        ValueError: If the GOOGLE_API_KEY environment variable is not set.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set.")
    genai.configure(api_key=api_key)

@retry_with_exponential_backoff()
def normalize_text(book_name: str, chapter: int, verse: int, verse_text: str, prompt_path: str) -> list[str]:
    """
    Normalizes a verse of text using a generative AI model.

    Args:
        verse_text: The text of the verse to normalize.
        prompt_path: The path to the file containing the prompt template.

    Returns:
        A list of strings, where each string is a decomposed proposition.
        Returns an empty list if an error occurs.
    """
    try:

        verse_text = str(verse_text)

        if verse_text == "nan":
            print(verse_text, "EMPTY VERSE")
            return []

        configure_api_key()

        with open(prompt_path) as f:
            prompt_template = f.read()

        model = genai.GenerativeModel(model_name="gemini-2.0-flash")

        final_prompt = prompt_template.format(verse_text=verse_text)

        response = model.generate_content(final_prompt)

        # The response text might be enclosed in markdown backticks for JSON
        cleaned_response_text = response.text.strip().replace('```json', '').replace('```', '').strip()
        print(f"Cleaned response text: {cleaned_response_text}")

        propositions = json.loads(cleaned_response_text)
        print(verse_text)
        print(propositions)
        return propositions
    except FileNotFoundError:
        print(f"Error: Prompt file not found at {prompt_path}")
        return []
    except ValueError as e:
        print(f"Configuration Error: {e}")
        return []

@retry_with_exponential_backoff()
def compare_verses(jps_norm: str, lxx_norm: str, prompt_path: str) -> list:
    """
    Compares two normalized verses using a generative AI model.

    Args:
        jps_norm: The normalized JPS verse.
        lxx_norm: The normalized LXX verse.
        prompt_path: The path to the file containing the prompt template.

    Returns:
        A list containing a boolean and a justification string.
        Returns an empty list if an error occurs.
    """
    try:
        if not jps_norm or jps_norm == '[]' or not lxx_norm or lxx_norm == '[]':
            return []

        configure_api_key()

        with open(prompt_path) as f:
            prompt_template = f.read()

        model = genai.GenerativeModel(model_name="gemini-2.0-flash")

        final_prompt = prompt_template + f"\n\nSource 1: JPS:\n\n{jps_norm}\n\nSource 2: LXX:\n\n{lxx_norm}"

        response = model.generate_content(final_prompt)

        cleaned_response_text = response.text.strip().replace('```json', '').replace('```', '').strip()

        comparison = json.loads(cleaned_response_text)
        return comparison
    except FileNotFoundError:
        print(f"Error: Prompt file not found at {prompt_path}")
        return []
    except Exception as e:
        print(f"An error occurred during comparison: {e}")
        return []
