from __future__ import annotations

from src.app.models import ToolAction


def draft_email(content: str) -> ToolAction:
    return ToolAction(
        name="draft_email",
        payload={"draft": content},
        executed=True,
    )
