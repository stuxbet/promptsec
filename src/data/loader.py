from __future__ import annotations

import json
from pathlib import Path

from src.app.models import ContentItem, Scenario


def synthetic_root(root: Path | None = None) -> Path:
    base = Path(root) if root else Path.cwd()
    return base / "synthetic_data"


def load_content_items(root: Path | None = None) -> dict[str, ContentItem]:
    base = synthetic_root(root)
    items: dict[str, ContentItem] = {}
    for folder in ("emails", "docs"):
        for path in sorted((base / folder).glob("*.json")):
            payload = json.loads(path.read_text())
            items[f"{folder}/{path.name}"] = ContentItem.model_validate(payload)
    return items


def load_scenarios(root: Path | None = None, scenario_set: str = "default") -> list[Scenario]:
    base = synthetic_root(root) / "scenarios"
    scenarios: list[Scenario] = []
    for path in sorted(base.glob("*.json")):
        payload = json.loads(path.read_text())
        if payload.get("scenario_set", "default") == scenario_set:
            payload.pop("scenario_set", None)
            scenarios.append(Scenario.model_validate(payload))
    return scenarios
