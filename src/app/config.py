from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(slots=True)
class Settings:
    model_backend: str = "mock"
    openai_base_url: str = "https://api.openai.com/v1"
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    output_dir: Path = Path("evidence/sample_outputs")
    log_level: str = "INFO"


def get_settings() -> Settings:
    return Settings(
        model_backend=os.getenv("MODEL_BACKEND", "mock"),
        openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        output_dir=Path(os.getenv("OUTPUT_DIR", "evidence/sample_outputs")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
