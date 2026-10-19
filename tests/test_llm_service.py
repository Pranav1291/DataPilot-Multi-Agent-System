
from unittest.mock import MagicMock, patch

import pytest

from datapilot.services.llm_service import ask_llm, get_llm


def test_get_llm_requires_api_key():
    # Simulate missing credentials without calling Groq.
    settings = MagicMock()
    settings.groq_api_key = None

    with (
        patch(
            "datapilot.services.llm_service.get_settings",
            return_value=settings,
        ),
        pytest.raises(ValueError, match="Groq API key is missing"),
    ):
        get_llm()    # Simulate missing credentials without calling Groq.
    settings = MagicMock()
    settings.groq_api_key = None

    with patch(
        "datapilot.services.llm_service.get_settings",
        return_value=settings,
    ), pytest.raises(ValueError, match="Groq API key is missing"):
        get_llm()


def test_ask_llm_rejects_empty_question():
    with pytest.raises(ValueError, match="Question cannot be empty"):
        ask_llm("   ")


def test_ask_llm_returns_model_response():
    mock_llm = MagicMock()
    mock_llm.invoke.return_value.content = "Hello from DataPilot!"

    with patch(
        "datapilot.services.llm_service.get_llm",
        return_value=mock_llm,
    ):
        result = ask_llm("Say hello")

    assert result == "Hello from DataPilot!"
    mock_llm.invoke.assert_called_once_with("Say hello")
