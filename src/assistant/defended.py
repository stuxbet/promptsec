from __future__ import annotations

from collections.abc import Callable

from src.app.models import AssistantResponse, RunLog, Scenario
from src.app.types import DecisionRoute, ResponseStatus
from src.assistant.approvals import review_action
from src.assistant.policy import evaluate_action_policy, evaluate_validation_policy
from src.assistant.prompts import build_defended_request
from src.assistant.tool_router import ToolRouter
from src.assistant.validators import run_validations
from src.data.retrieval import retrieve_items
from src.llm.interface import GemmaModel


class DefendedAssistant:
    def __init__(self, model: GemmaModel) -> None:
        self.model = model
        self.tool_router = ToolRouter(allow_unknown_actions=False)

    def run(
        self,
        scenario: Scenario,
        all_items: dict[str, object],
        progress_callback: Callable[[str], None] | None = None,
    ) -> AssistantResponse:
        retrieved_items = retrieve_items(
            user_request=scenario.user_request,
            items=all_items,
            preferred_paths=scenario.relevant_data_files,
        )
        if progress_callback is not None:
            progress_callback(f"retrieved {len(retrieved_items)} context items")
        model_request = build_defended_request(scenario.user_request, retrieved_items)
        model_response = self.model.generate(model_request, progress_callback=progress_callback)

        action_policy = evaluate_action_policy(model_response.action_name, retrieved_items, scenario.user_request)
        if not action_policy.allowed:
            blocked_content = f"Blocked by policy: {action_policy.reason}"
            run_log = RunLog(
                scenario_id=scenario.scenario_id,
                assistant_name="defended",
                user_request=scenario.user_request,
                prompt_style=model_request.prompt_style,
                retrieved_items=retrieved_items,
                proposed_action=model_response.action_name,
                policy_decision=action_policy,
                final_action="refuse",
                final_status=ResponseStatus.BLOCKED,
                notes=model_response.notes,
            )
            return AssistantResponse(
                assistant_name="defended",
                action_name="refuse",
                status=ResponseStatus.BLOCKED,
                content=blocked_content,
                rationale=action_policy.reason,
                policy_decision=action_policy,
                retrieved_items=retrieved_items,
                run_log=run_log,
            )

        provisional = AssistantResponse(
            assistant_name="defended",
            action_name=model_response.action_name,
            status=ResponseStatus.COMPLETED,
            content=model_response.content,
            rationale="Provisional result pending defended validation and approval checks.",
            policy_decision=action_policy,
            retrieved_items=retrieved_items,
            run_log=RunLog(
                scenario_id=scenario.scenario_id,
                assistant_name="defended",
                user_request=scenario.user_request,
                prompt_style=model_request.prompt_style,
                retrieved_items=retrieved_items,
                proposed_action=model_response.action_name,
                policy_decision=action_policy,
                final_action=model_response.action_name,
                final_status=ResponseStatus.COMPLETED,
                notes=model_response.notes,
            ),
        )
        findings = run_validations(provisional, scenario.user_request, retrieved_items)
        validation_policy = evaluate_validation_policy(model_response.action_name, findings)

        if validation_policy.route == DecisionRoute.BLOCK:
            run_log = provisional.run_log.model_copy(
                update={
                    "validation_findings": findings,
                    "policy_decision": validation_policy,
                    "final_action": "refuse",
                    "final_status": ResponseStatus.BLOCKED,
                }
            )
            return AssistantResponse(
                assistant_name="defended",
                action_name="refuse",
                status=ResponseStatus.BLOCKED,
                content=f"Blocked by defended validation: {validation_policy.reason}",
                rationale=validation_policy.reason,
                policy_decision=validation_policy,
                validation_findings=findings,
                retrieved_items=retrieved_items,
                run_log=run_log,
            )

        if validation_policy.route == DecisionRoute.REVIEW:
            safe_content = "Flag for review: retrieved content may be attempting to steer the assistant away from the user request."
            tool_action = self.tool_router.execute("flag_for_review", safe_content)
            run_log = provisional.run_log.model_copy(
                update={
                    "validation_findings": findings,
                    "policy_decision": validation_policy,
                    "final_action": "flag_for_review",
                    "final_status": ResponseStatus.COMPLETED,
                }
            )
            return AssistantResponse(
                assistant_name="defended",
                action_name="flag_for_review",
                status=ResponseStatus.COMPLETED,
                content=safe_content,
                rationale=validation_policy.reason,
                tool_action=tool_action,
                policy_decision=validation_policy,
                validation_findings=findings,
                retrieved_items=retrieved_items,
                run_log=run_log,
            )

        approval = review_action(model_response.action_name, scenario.user_request, retrieved_items)
        if approval.required and not approval.approved:
            run_log = provisional.run_log.model_copy(
                update={
                    "validation_findings": findings,
                    "approval_decision": approval,
                    "final_action": model_response.action_name,
                    "final_status": ResponseStatus.NEEDS_APPROVAL,
                }
            )
            return AssistantResponse(
                assistant_name="defended",
                action_name=model_response.action_name,
                status=ResponseStatus.NEEDS_APPROVAL,
                content="Draft prepared but held for simulated human approval because confidential content affects an external-facing response.",
                rationale=approval.reason,
                policy_decision=action_policy,
                validation_findings=findings,
                approval_decision=approval,
                retrieved_items=retrieved_items,
                run_log=run_log,
            )

        tool_action = self.tool_router.execute(model_response.action_name, model_response.content)
        run_log = provisional.run_log.model_copy(
            update={
                "validation_findings": findings,
                "approval_decision": approval,
                "final_action": model_response.action_name,
                "final_status": ResponseStatus.COMPLETED,
            }
        )
        return AssistantResponse(
            assistant_name="defended",
            action_name=model_response.action_name,
            status=ResponseStatus.COMPLETED,
            content=model_response.content,
            rationale="Defended assistant completed the request after policy, validation, and approval checks.",
            tool_action=tool_action,
            policy_decision=action_policy,
            validation_findings=findings,
            approval_decision=approval,
            retrieved_items=retrieved_items,
            run_log=run_log,
        )
