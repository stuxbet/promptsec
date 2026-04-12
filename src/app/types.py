from __future__ import annotations

from enum import StrEnum


class ContentType(StrEnum):
    EMAIL = "email"
    DOC = "doc"


class TrustLevel(StrEnum):
    TRUSTED = "trusted"
    UNTRUSTED = "untrusted"
    UNKNOWN = "unknown"


class SensitivityLevel(StrEnum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"


class ExpectedBehavior(StrEnum):
    SUMMARIZE = "summarize"
    DRAFT_SAFE = "draft_safe"
    FLAG_REVIEW = "flag_review"
    REFUSE = "refuse"
    REQUIRES_APPROVAL = "requires_approval"


class ScenarioCategory(StrEnum):
    BENIGN = "benign"
    EDGE_CASE = "edge_case"
    INSTRUCTION_OVERRIDE = "instruction_override"
    DATA_EXFILTRATION = "data_exfiltration_attempt"
    TOOL_MISUSE = "tool_misuse_attempt"
    SUMMARY_POISONING = "summary_poisoning"
    APPROVAL_BYPASS = "approval_bypass_attempt"


class AssistantAction(StrEnum):
    SUMMARIZE = "summarize"
    DRAFT_RESPONSE = "draft_response"
    FLAG_FOR_REVIEW = "flag_for_review"
    REFUSE = "refuse"
    SEND_EXTERNAL_EMAIL = "send_external_email"
    EXPORT_DATA = "export_data"
    RUN_COMMAND = "run_command"


class ResponseStatus(StrEnum):
    COMPLETED = "completed"
    BLOCKED = "blocked"
    NEEDS_APPROVAL = "needs_approval"
    ERROR = "error"


class DecisionRoute(StrEnum):
    ALLOW = "allow"
    BLOCK = "block"
    REVIEW = "review"
