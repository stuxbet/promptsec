from __future__ import annotations

from src.app.models import RetrievedItem, ToolAction


def read_email(item: RetrievedItem) -> ToolAction:
    return ToolAction(
        name="read_email",
        payload={"item_id": item.item.id, "content": item.item.content},
        executed=True,
    )
