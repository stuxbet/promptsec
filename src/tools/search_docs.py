from __future__ import annotations

from src.app.models import RetrievedItem, ToolAction


def search_docs(items: list[RetrievedItem]) -> ToolAction:
    return ToolAction(
        name="search_docs",
        payload={"hits": [item.item.id for item in items]},
        executed=True,
    )
