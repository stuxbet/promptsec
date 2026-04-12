from __future__ import annotations

from collections.abc import Callable
import json
import re

import httpx

from src.app.config import Settings
from src.app.models import ModelRequest, ModelResponse

CODE_FENCE_OPEN_RE = re.compile(r"^```(?:json)?\s*\n?", re.IGNORECASE)
CODE_FENCE_CLOSE_RE = re.compile(r"\n?```\s*$")


class GemmaModel:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def generate(
        self,
        request: ModelRequest,
        progress_callback: Callable[[str], None] | None = None,
    ) -> ModelResponse:
        url = self._settings.llm_base_url.rstrip("/")
        if not url.endswith("/chat/completions"):
            url = f"{url}/chat/completions" if url.endswith("/v1") else f"{url}/v1/chat/completions"

        messages = [msg.model_dump(mode="json") for msg in request.messages]
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

        if progress_callback is not None:
            progress_callback(
                f"sending request to {self._settings.llm_model} at {url} "
                f"(timeout={self._settings.llm_timeout_seconds:.0f}s)"
            )

        try:
            response = httpx.post(
                url,
                headers={"Content-Type": "application/json"},
                json={
                    "model": self._settings.llm_model,
                    "messages": messages,
                    "temperature": 0,
                },
                timeout=self._settings.llm_timeout_seconds,
            )
        except httpx.HTTPError:
            if progress_callback is not None:
                progress_callback("model request failed before a response was received")
            raise

        if progress_callback is not None:
            progress_callback(f"received HTTP {response.status_code} from model endpoint")
        response.raise_for_status()
        data = response.json()
        raw_content = data["choices"][0]["message"]["content"]

        # Strip markdown code fences that Gemma often wraps around JSON
        stripped = CODE_FENCE_OPEN_RE.sub("", raw_content.strip())
        stripped = CODE_FENCE_CLOSE_RE.sub("", stripped).strip()

        try:
            payload = json.loads(stripped)
            if progress_callback is not None:
                progress_callback(f"parsed model response -> action={payload.get('action_name', 'unknown')}")
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
            if progress_callback is not None:
                progress_callback(f"parsed fallback model response -> action={action_name}")
            return ModelResponse(action_name=action_name, content=raw_content, notes=["Parsed fallback from non-JSON response."])
