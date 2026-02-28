import os

import httpx


OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
DEFAULT_FREE_MODEL = "meta-llama/llama-3.3-8b-instruct:free"
FALLBACK_FREE_MODELS = [
    "stepfun/step-3.5-flash:free",
    "arcee-ai/trinity-large-preview:free",
    "upstage/solar-pro-3:free",
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "openai/gpt-oss-20b:free",
    "openai/gpt-oss-120b:free",
    DEFAULT_FREE_MODEL,
]


def get_openrouter_model() -> str:
    return os.getenv("OPENROUTER_MODEL", DEFAULT_FREE_MODEL)


def get_available_free_models() -> list[str]:
    try:
        response = httpx.get(OPENROUTER_MODELS_URL, timeout=20.0)
    except httpx.HTTPError:
        return []

    if response.status_code >= 400:
        return []

    try:
        payload = response.json()
    except ValueError:
        return []

    data = payload.get("data")
    if not isinstance(data, list):
        return []

    free_models: list[str] = []
    for entry in data:
        model_id = entry.get("id") if isinstance(entry, dict) else None
        if isinstance(model_id, str) and model_id.endswith(":free"):
            free_models.append(model_id)

    return free_models


def build_model_candidates() -> list[str]:
    configured_model = os.getenv("OPENROUTER_MODEL")
    if configured_model:
        return [configured_model]

    available = get_available_free_models()
    if not available:
        return FALLBACK_FREE_MODELS

    preferred = [model for model in FALLBACK_FREE_MODELS if model in available]
    remaining = [model for model in available if model not in preferred]

    return preferred + remaining


def ask_openrouter(prompt: str) -> tuple[str, str]:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not configured")

    models_to_try = build_model_candidates()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    last_error: str | None = None

    for model in models_to_try:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }

        try:
            response = httpx.post(
                OPENROUTER_CHAT_URL,
                headers=headers,
                json=payload,
                timeout=45.0,
            )
        except httpx.HTTPError as exc:
            last_error = f"OpenRouter request failed: {exc}"
            continue

        if response.status_code >= 400:
            text = response.text[:300]
            if response.status_code == 404 and "No endpoints found" in text:
                last_error = f"Model unavailable: {model}"
                continue

            raise RuntimeError(f"OpenRouter error {response.status_code}: {text}")

        data = response.json()
        choices = data.get("choices") or []
        if not choices:
            last_error = f"OpenRouter returned no choices for model {model}"
            continue

        message = choices[0].get("message") or {}
        content = message.get("content")
        if isinstance(content, str) and content.strip():
            return content.strip(), model

        last_error = f"OpenRouter returned empty content for model {model}"

    raise RuntimeError(last_error or "No available OpenRouter model responded")


def connectivity_test() -> dict[str, str]:
    prompt = "2+2"
    response, model = ask_openrouter(prompt)
    return {
        "model": model,
        "prompt": prompt,
        "response": response,
    }
