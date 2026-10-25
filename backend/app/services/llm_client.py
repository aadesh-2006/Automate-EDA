import os

import httpx


class LLMConfigurationError(ValueError):
    """Raised when the hosted LLM client is not configured."""


class LLMProviderError(RuntimeError):
    """Raised when the hosted LLM provider fails or returns invalid data."""


def get_llm_config() -> dict[str, str]:
    """Read and validate OpenAI-compatible API settings from environment."""
    config = {
        "base_url": os.getenv("LLM_BASE_URL", "").strip().rstrip("/"),
        "api_key": os.getenv("LLM_API_KEY", "").strip(),
        "model": os.getenv("LLM_MODEL", "").strip(),
    }

    missing = [name for name, value in config.items() if not value]
    if missing:
        raise LLMConfigurationError(
            "Missing LLM configuration: " + ", ".join(missing)
        )

    return config


async def generate_chat_completion(
    system_prompt: str,
    user_prompt: str,
    timeout_seconds: float = 30.0,
) -> str:
    """Request a chat completion from an OpenAI-compatible provider."""
    config = get_llm_config()
    url = f"{config['base_url']}/chat/completions"

    payload = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
    }

    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {config['api_key']}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as exc:
        raise LLMProviderError(
            f"LLM provider returned HTTP {exc.response.status_code}."
        ) from exc
    except httpx.TimeoutException as exc:
        raise LLMProviderError("LLM provider request timed out.") from exc
    except httpx.RequestError as exc:
        raise LLMProviderError("Could not connect to the LLM provider.") from exc
    except ValueError as exc:
        raise LLMProviderError("LLM provider returned invalid JSON.") from exc

    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMProviderError(
            "LLM provider response did not contain a chat completion."
        ) from exc

    if not isinstance(content, str) or not content.strip():
        raise LLMProviderError("LLM provider returned empty completion text.")

    return content.strip()
