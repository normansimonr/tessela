import pytest
from unittest.mock import patch, MagicMock
from backend.src.normalization_service import NormalizationService

@pytest.fixture
def mock_genai_model():
    with patch("google.generativeai.GenerativeModel") as mock_model_class:
        mock_instance = MagicMock()
        mock_model_class.return_value = mock_instance
        yield mock_instance

def test_normalization_service_initialization():
    with patch("google.generativeai.configure") as mock_configure:
        service = NormalizationService(api_key="test_api_key")
        mock_configure.assert_called_once_with(api_key="test_api_key")
        assert service.model is not None

def test_normalize_text_success(mock_genai_model):
    mock_genai_model.generate_content.return_value.text = "Normalized text output."
    service = NormalizationService(api_key="test_api_key")
    
    original_text = "This is some old text."
    normalized_text = service.normalize_text(original_text)
    
    mock_genai_model.generate_content.assert_called_once()
    assert "Normalize the following biblical text" in mock_genai_model.generate_content.call_args[0][0]
    assert original_text in mock_genai_model.generate_content.call_args[0][0]
    assert normalized_text == "Normalized text output."

def test_normalize_text_empty_input():
    service = NormalizationService(api_key="test_api_key")
    normalized_text = service.normalize_text("")
    assert normalized_text is None

def test_normalize_text_none_input():
    service = NormalizationService(api_key="test_api_key")
    normalized_text = service.normalize_text(None)
    assert normalized_text is None

def test_normalize_text_api_error(mock_genai_model):
    mock_genai_model.generate_content.side_effect = Exception("API error")
    service = NormalizationService(api_key="test_api_key")
    
    original_text = "Text causing error."
    normalized_text = service.normalize_text(original_text)
    
    assert normalized_text is None
