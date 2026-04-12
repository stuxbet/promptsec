from __future__ import annotations

from src.app.models import ToolAction


def flag_review(reason: str) -> ToolAction:
    return ToolAction(
        name="flag_review",
        payload={"reason": reason},
        executed=True,
    )
