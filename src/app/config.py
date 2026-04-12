from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(slots=True)
class Settings:
    llm_mode: str = "offline"
    llm_base_url: str | None = None
    llm_model: str = "gemma4:latest"
    llm_api_key: str = ""
    llm_timeout_seconds: float = 20.0
    output_dir: Path = Path("evidence/sample_outputs")
    log_level: str = "INFO"


def get_settings() -> Settings:
    legacy_backend = os.getenv("MODEL_BACKEND", "").strip().lower()
    llm_mode = os.getenv("LLM_MODE", "").strip().lower()
    if not llm_mode:
        llm_mode = "http" if legacy_backend == "openai_compatible" else "offline"

    return Settings(
        llm_mode=llm_mode,
        llm_base_url=((os.getenv("LLM_BASE_URL") or os.getenv("OPENAI_BASE_URL") or "").strip() or None),
        llm_model=(os.getenv("LLM_MODEL") or os.getenv("OPENAI_MODEL") or "gemma4:latest").strip(),
        llm_api_key=(os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or "").strip(),
        llm_timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "20")),
        output_dir=Path(os.getenv("OUTPUT_DIR", "evidence/sample_outputs")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
