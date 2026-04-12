from __future__ import annotations

import json

import httpx

from src.app.config import Settings
from src.app.models import ModelRequest, ModelResponse


class OpenAICompatibleModel:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def generate(self, request: ModelRequest) -> ModelResponse:
        if not self._settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for the openai_compatible backend.")

        url = self._settings.openai_base_url.rstrip("/")
        if not url.endswith("/chat/completions"):
            url = f"{url}/chat/completions" if url.endswith("/v1") else f"{url}/v1/chat/completions"

        messages = [message.model_dump(mode="json") for message in request.messages]
        messages.insert(
            0,
            {
                "role": "system",
                "content": (
                    "Return JSON with keys action_name and content. "
                    "Allowed action_name values are summarize, draft_response, flag_for_review, or refuse."
                ),
            },
        )

        response = httpx.post(
            url,
            headers={
                "Authorization": f"Bearer {self._settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self._settings.openai_model,
                "messages": messages,
                "temperature": 0,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        raw_content = data["choices"][0]["message"]["content"]
        try:
            payload = json.loads(raw_content)
            return ModelResponse.model_validate(payload)
        except json.JSONDecodeError:
            lowered = raw_content.lower()
            action_name = "summarize"
            if "flag for review" in lowered:
                action_name = "flag_for_review"
            elif "draft" in lowered or "reply" in lowered:
                action_name = "draft_response"
            elif "refuse" in lowered or "cannot" in lowered:
                action_name = "refuse"
            return ModelResponse(action_name=action_name, content=raw_content, notes=["Parsed fallback text response."])
