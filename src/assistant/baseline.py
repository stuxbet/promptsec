from __future__ import annotations

from src.app.models import AssistantResponse, RunLog, Scenario
from src.app.types import ResponseStatus
from src.assistant.prompts import build_baseline_request
from src.assistant.tool_router import ToolRouter
from src.data.retrieval import retrieve_items
from src.llm.interface import GemmaModel


class BaselineAssistant:
    def __init__(self, model: GemmaModel) -> None:
        self.model = model
        self.tool_router = ToolRouter(allow_unknown_actions=True)

    def run(self, scenario: Scenario, all_items: dict[str, object]) -> AssistantResponse:
        retrieved_items = retrieve_items(
            user_request=scenario.user_request,
            items=all_items,
            preferred_paths=scenario.relevant_data_files,
        )
        model_request = build_baseline_request(scenario.user_request, retrieved_items)
        model_response = self.model.generate(model_request)
        tool_action = self.tool_router.execute(model_response.action_name, model_response.content)
        run_log = RunLog(
            scenario_id=scenario.scenario_id,
            assistant_name="baseline",
            user_request=scenario.user_request,
            prompt_style=model_request.prompt_style,
            retrieved_items=retrieved_items,
            proposed_action=model_response.action_name,
            final_action=model_response.action_name,
            final_status=ResponseStatus.COMPLETED,
            notes=model_response.notes,
        )
        return AssistantResponse(
            assistant_name="baseline",
            action_name=model_response.action_name,
            status=ResponseStatus.COMPLETED,
            content=model_response.content,
            rationale="Baseline assistant executed the model output without layered defenses.",
            tool_action=tool_action,
            retrieved_items=retrieved_items,
            run_log=run_log,
        )
