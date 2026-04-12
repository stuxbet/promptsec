from __future__ import annotations

from abc import ABC, abstractmethod

from src.app.config import Settings
from src.app.models import ModelRequest, ModelResponse


class ModelBackend(ABC):
    @abstractmethod
    def generate(self, request: ModelRequest) -> ModelResponse:
        raise NotImplementedError


def create_model_backend(settings: Settings) -> ModelBackend:
    if settings.model_backend == "openai_compatible":
        from src.llm.openai_compatible import OpenAICompatibleModel

        return OpenAICompatibleModel(settings)
    from src.llm.mock_model import MockModel

    return MockModel()
