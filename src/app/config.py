from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


def _read_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        if key:
            values[key] = value
    return values


@dataclass(slots=True)
class Settings:
    llm_base_url: str = "http://172.27.112.1:11434/v1"
    llm_model: str = "gemma4:latest"
    llm_timeout_seconds: float = 300.0
    output_dir: Path = Path("evidence/sample_outputs")
    log_level: str = "INFO"


def get_settings() -> Settings:
    env_file_values = _read_dotenv(Path.cwd() / ".env")

    def lookup(name: str, default: str = "") -> str:
        return os.getenv(name, env_file_values.get(name, default))

    return Settings(
        llm_base_url=lookup("LLM_BASE_URL", "http://172.27.112.1:11434/v1"),
        llm_model=lookup("LLM_MODEL", "gemma4:latest"),
        llm_timeout_seconds=float(lookup("LLM_TIMEOUT_SECONDS", "300")),
        output_dir=Path(lookup("OUTPUT_DIR", "evidence/sample_outputs")),
        log_level=lookup("LOG_LEVEL", "INFO"),
    )
