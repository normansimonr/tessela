import google.generativeai as genai
import json
import os
from typing import Optional, List

class NormalizationService:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.normalization_prompt = self._load_normalization_prompt()

    def _load_normalization_prompt(self) -> str:
        """Loads the normalization prompt from the file system."""
        try:
            # Construct the absolute path to the prompt file
            current_dir = os.path.dirname(__file__)
            # Assuming prompts directory is at the project root, two levels up from backend/src
            prompt_path = os.path.join(current_dir, "..", "..", "..", "prompts", "normalization_prompt.txt")
            # Normalize the path to handle '..'
            absolute_prompt_path = os.path.abspath(prompt_path)

            with open(absolute_prompt_path, "r") as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: normalization_prompt.txt not found at {absolute_prompt_path}.")
            return ""

    def decompose_text(self, text: str) -> Optional[List[str]]:
        """
        Performs deep semantic decomposition on the given text using the configured generative AI model.
        """
        if not text:
            return None
        try:
            prompt = self.normalization_prompt.format(verse_text=text)
            response = self.model.generate_content(prompt)
            # Assuming the model returns a JSON string
            return json.loads(response.text)
        except Exception as e:
            print(f"Error during deep semantic decomposition: {e}")
            return None
