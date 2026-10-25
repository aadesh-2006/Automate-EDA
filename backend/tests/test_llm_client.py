
import asyncio
import json

import httpx
import pytest

from app.services.llm_client import (
    LLMConfigurationError,
    LLMProviderError,
    generate_chat_completion,
    get_llm_config,
)


def test_get_llm_config_reads_environment_variables(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "https://example.com/v1/")
    monkeypatch.setenv("LLM_API_KEY", "test-token")
    monkeypatch.setenv("LLM_MODEL", "test-model")

    config = get_llm_config()

    assert config == {
        "base_url": "https://example.com/v1",
        "api_key": "test-token",
        "model": "test-model",
    }


def test_get_llm_config_rejects_missing_variables(monkeypatch):
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)

    with pytest.raises(
        LLMConfigurationError,
        match="Missing LLM configuration",
    ):
        get_llm_config()


def test_get_llm_config_rejects_blank_values(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", " ")
    monkeypatch.setenv("LLM_API_KEY", " ")
    monkeypatch.setenv("LLM_MODEL", " ")

    with pytest.raises(LLMConfigurationError):
        get_llm_config()


def test_generate_chat_completion_returns_assistant_text(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "https://example.com/v1")
    monkeypatch.setenv("LLM_API_KEY", "test-token")
    monkeypatch.setenv("LLM_MODEL", "test-model")

    def mock_handler(request):
        assert str(request.url) == "https://example.com/v1/chat/completions"
        assert request.headers["Authorization"] == "Bearer test-token"

        payload = json.loads(request.content)
        assert payload["model"] == "test-model"
        assert payload["messages"][0]["role"] == "system"
        assert payload["messages"][1]["content"] == "Analyze this evidence."

        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "  Two columns found.  "}}]},
        )

    original_client = httpx.AsyncClient
    transport = httpx.MockTransport(mock_handler)

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kwargs: original_client(transport=transport, **kwargs),
    )

    result = asyncio.run(
        generate_chat_completion("You are an analyst.", "Analyze this evidence.")
    )

    assert result == "Two columns found."


def test_generate_chat_completion_handles_provider_http_error(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "https://example.com/v1")
    monkeypatch.setenv("LLM_API_KEY", "test-token")
    monkeypatch.setenv("LLM_MODEL", "test-model")

    transport = httpx.MockTransport(
        lambda request: httpx.Response(503, text="Unavailable")
    )
    original_client = httpx.AsyncClient

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kwargs: original_client(transport=transport, **kwargs),
    )

    with pytest.raises(LLMProviderError, match="HTTP 503"):
        asyncio.run(generate_chat_completion("system", "user"))


def test_generate_chat_completion_rejects_malformed_response(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "https://example.com/v1")
    monkeypatch.setenv("LLM_API_KEY", "test-token")
    monkeypatch.setenv("LLM_MODEL", "test-model")

    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json={"unexpected": []})
    )
    original_client = httpx.AsyncClient

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kwargs: original_client(transport=transport, **kwargs),
    )

    with pytest.raises(LLMProviderError, match="did not contain"):
        asyncio.run(generate_chat_completion("system", "user"))
