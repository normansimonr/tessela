import unittest
from unittest.mock import patch, MagicMock
import os

# This import will fail until we create the file in the next step
from src.normalization_service import normalize_text

class TestNormalizationService(unittest.TestCase):

    def setUp(self):
        """Set up a dummy prompt file."""
        self.prompt_path = 'tests/dummy_prompt.txt'
        with open(self.prompt_path, 'w') as f:
            f.write("Decompose this: {verse_text}")

    def tearDown(self):
        """Remove the dummy prompt file."""
        if os.path.exists(self.prompt_path):
            os.remove(self.prompt_path)

    @patch('src.normalization_service.configure_api_key')
    @patch('google.generativeai.GenerativeModel')
    def test_normalize_text(self, MockGenerativeModel, MockConfigureApiKey):
        """
        Test that the normalization service correctly calls the AI model
        and parses its response.
        """
        # Arrange: Set up the mock response from the AI model
        mock_response = MagicMock()
        mock_response.text = '["Proposition 1.", "Proposition 2."]'
        
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.return_value = mock_response
        MockGenerativeModel.return_value = mock_model_instance

        verse_text = "This is a test verse."
        
        # Act: Call the function we are testing
        propositions = normalize_text(verse_text, self.prompt_path)

        # Assert: Check that the function behaved as expected
        self.assertEqual(propositions, ["Proposition 1.", "Proposition 2."])
        
        # Check that the model was initialized and called correctly
        MockGenerativeModel.assert_called_with(model_name="gemini-2.5-pro")
        
        expected_prompt = f"Decompose this: {verse_text}"
        mock_model_instance.generate_content.assert_called_once_with(expected_prompt)

if __name__ == '__main__':
    unittest.main()
