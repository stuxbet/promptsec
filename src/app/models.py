from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from src.app.types import (
    AssistantAction,
    ContentType,
    DecisionRoute,
    ExpectedBehavior,
    ResponseStatus,
    ScenarioCategory,
    SensitivityLevel,
    TrustLevel,
)


class ContentItem(BaseModel):
    id: str
    type: ContentType
    trust_level: TrustLevel
    sensitivity: SensitivityLevel
    content: str
    tags: list[str] = Field(default_factory=list)
    expected_behavior: ExpectedBehavior
    attack_goal: str | None = None


class Scenario(BaseModel):
    scenario_id: str
    user_request: str
    relevant_data_files: list[str]
    expected_safe_behavior: ExpectedBehavior
    unsafe_behavior_to_avoid: str
    attack_category: ScenarioCategory
    sensitivity_level: SensitivityLevel


class RetrievedItem(BaseModel):
    path: str
    score: float
    item: ContentItem
    source_label: TrustLevel


class PromptMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ModelRequest(BaseModel):
    messages: list[PromptMessage]
    user_request: str
    retrieved_items: list[RetrievedItem]
    available_actions: list[AssistantAction]
    prompt_style: Literal["merged", "separated"]


class ModelResponse(BaseModel):
    action_name: str
    content: str
    notes: list[str] = Field(default_factory=list)


class ToolAction(BaseModel):
    name: str
    payload: dict[str, Any] = Field(default_factory=dict)
    risky: bool = False
    executed: bool = False


class PolicyDecision(BaseModel):
    action_name: str
    allowed: bool
    route: DecisionRoute
    requires_approval: bool = False
    reason: str


class ValidationFinding(BaseModel):
    code: str
    severity: Literal["info", "warning", "high"]
    message: str


class ApprovalDecision(BaseModel):
    required: bool
    approved: bool
    reason: str


class RunLog(BaseModel):
    scenario_id: str
    assistant_name: str
    user_request: str
    prompt_style: str
    retrieved_items: list[RetrievedItem] = Field(default_factory=list)
    proposed_action: str
    policy_decision: PolicyDecision | None = None
    validation_findings: list[ValidationFinding] = Field(default_factory=list)
    approval_decision: ApprovalDecision | None = None
    final_action: str
    final_status: ResponseStatus
    notes: list[str] = Field(default_factory=list)


class AssistantResponse(BaseModel):
    assistant_name: str
    action_name: str
    status: ResponseStatus
    content: str
    rationale: str
    tool_action: ToolAction | None = None
    policy_decision: PolicyDecision | None = None
    validation_findings: list[ValidationFinding] = Field(default_factory=list)
    approval_decision: ApprovalDecision | None = None
    retrieved_items: list[RetrievedItem] = Field(default_factory=list)
    run_log: RunLog


class ScenarioResult(BaseModel):
    scenario_id: str
    assistant_name: str
    status: ResponseStatus
    action_name: str
    expected_behavior: ExpectedBehavior
    safe: bool
    task_success: bool
    attack_success: bool
    leakage_detected: bool
    blocked_unsafe: bool
    false_positive: bool
    notes: str
    response_excerpt: str
    findings: list[ValidationFinding] = Field(default_factory=list)
    run_log: RunLog


class MetricSummary(BaseModel):
    attack_success_rate: float
    benign_task_success_rate: float
    leakage_rate: float
    blocked_unsafe_action_rate: float
    false_positive_rate: float


class EvaluationSummary(BaseModel):
    scenario_set: str
    metrics: dict[str, MetricSummary]
    results: dict[str, list[ScenarioResult]]
