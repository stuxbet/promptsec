from __future__ import annotations

import re
from typing import Iterable

from src.app.models import ContentItem, RetrievedItem


TOKEN_RE = re.compile(r"[a-z0-9_]+")


def tokenize(text: str) -> set[str]:
    return set(TOKEN_RE.findall(text.lower()))


def score_item(query_tokens: set[str], item: ContentItem) -> float:
    content_tokens = tokenize(item.content)
    tag_tokens = tokenize(" ".join(item.tags))
    overlap = len(query_tokens & content_tokens)
    tag_overlap = len(query_tokens & tag_tokens) * 1.5
    sensitivity_bonus = 0.25 if item.sensitivity.value in query_tokens else 0.0
    return overlap + tag_overlap + sensitivity_bonus


def retrieve_items(
    user_request: str,
    items: dict[str, ContentItem],
    preferred_paths: Iterable[str] | None = None,
    top_k: int = 4,
) -> list[RetrievedItem]:
    preferred = set(preferred_paths or [])
    query_tokens = tokenize(user_request)
    candidate_items = items
    if preferred:
        candidate_items = {path: item for path, item in items.items() if path in preferred}

    ranked: list[tuple[str, float, ContentItem]] = []
    for path, item in candidate_items.items():
        score = score_item(query_tokens, item)
        if path in preferred:
            score += 5.0
        if score > 0 or path in preferred:
            ranked.append((path, score, item))
    ranked.sort(key=lambda row: (-row[1], row[0]))
    selected = ranked[:top_k]
    return [
        RetrievedItem(path=path, score=round(score, 2), item=item, source_label=item.trust_level)
        for path, score, item in selected
    ]
