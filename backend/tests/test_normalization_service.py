import pytest
from unittest.mock import patch, MagicMock
from backend.src.normalization_service import NormalizationService
import json

@pytest.fixture
def mock_genai_model():
    with patch("google.generativeai.GenerativeModel") as mock_model_class:
        mock_instance = MagicMock()
        mock_model_class.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_load_normalization_prompt():
    with patch.object(NormalizationService, '_load_normalization_prompt') as mock_method:
        mock_method.return_value = "Verse: {verse_text}\nOutput:"
        yield mock_method

def test_normalization_service_initialization(mock_load_normalization_prompt):
    with patch("google.generativeai.configure") as mock_configure:
        service = NormalizationService(api_key="test_api_key")
        mock_configure.assert_called_once_with(api_key="test_api_key")
        assert service.model is not None
        mock_load_normalization_prompt.assert_called_once()

def test_decompose_text_success(mock_genai_model, mock_load_normalization_prompt):
    expected_output = ["God said a command.", "God commanded that light should exist.", "Light came to exist."]
    mock_genai_model.generate_content.return_value.text = json.dumps(expected_output)
    service = NormalizationService(api_key="test_api_key")
    
    original_text = "God said, ‘Let there be light,’ and there was light."
    decomposed_text = service.decompose_text(original_text)
    
    mock_genai_model.generate_content.assert_called_once()
    assert f"Verse: {original_text}\nOutput:" in mock_genai_model.generate_content.call_args[0][0]
    assert decomposed_text == expected_output

def test_decompose_text_empty_input(mock_load_normalization_prompt):
    service = NormalizationService(api_key="test_api_key")
    decomposed_text = service.decompose_text("")
    assert decomposed_text is None

def test_decompose_text_none_input(mock_load_normalization_prompt):
    service = NormalizationService(api_key="test_api_key")
    decomposed_text = service.decompose_text(None)
    assert decomposed_text is None

def test_decompose_text_api_error(mock_genai_model, mock_load_normalization_prompt):
    mock_genai_model.generate_content.side_effect = Exception("API error")
    service = NormalizationService(api_key="test_api_key")
    
    original_text = "Text causing error."
    decomposed_text = service.decompose_text(original_text)
    
    assert decomposed_text is None

def test_decompose_text_invalid_json_output(mock_genai_model, mock_load_normalization_prompt):
    mock_genai_model.generate_content.return_value.text = "This is not valid JSON."
    service = NormalizationService(api_key="test_api_key")
    
    original_text = "Some text."
    decomposed_text = service.decompose_text(original_text)
    
    assert decomposed_text is None
