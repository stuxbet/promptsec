from __future__ import annotations

from src.app.models import ToolAction
from src.tools.draft_email import draft_email
from src.tools.flag_review import flag_review


class ToolRouter:
    def __init__(self, allow_unknown_actions: bool) -> None:
        self.allow_unknown_actions = allow_unknown_actions

    def execute(self, action_name: str, content: str) -> ToolAction:
        if action_name == "summarize":
            return ToolAction(name="summarize", payload={"summary": content}, executed=True)
        if action_name == "draft_response":
            return draft_email(content)
        if action_name == "flag_for_review":
            return flag_review(content)
        if action_name == "refuse":
            return ToolAction(name="refuse", payload={"message": content}, executed=True)
        if self.allow_unknown_actions:
            return ToolAction(name=action_name, payload={"simulated": True, "detail": content}, risky=True, executed=True)
        return ToolAction(name=action_name, payload={"blocked": True, "detail": content}, risky=True, executed=False)
