import google.generativeai as genai
from typing import Optional

class NormalizationService:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def normalize_text(self, text: str) -> Optional[str]:
        """
        Normalizes the given text using the configured generative AI model.
        """
        if not text:
            return None
        try:
            # For demonstration, a simple prompt. In a real scenario,
            # the prompt would be more sophisticated and potentially loaded from a file.
            prompt = f"Normalize the following biblical text, correcting any spelling or grammatical errors, and standardizing archaic language to modern English where appropriate, while preserving its original meaning:\n\n'{text}'\n\nNormalized text:"
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error during normalization: {e}")
            return None
