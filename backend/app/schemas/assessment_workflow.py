from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class AssessmentWorkflowTransitionRequest(BaseModel):
    action: str = Field(min_length=3, max_length=100)
    comment: str | None = None
    external_reference: str | None = None
    assessment_unit: str | None = None


class AssessmentWorkflowEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: int
    profile_id: int
    from_status: str | None = None
    to_status: str
    action: str
    actor_role: str | None = None
    comment: str | None = None
    external_reference: str | None = None
    assessment_unit: str | None = None
    created_by: int | None = None
    occurred_at: datetime
    created_at: datetime
    updated_at: datetime


class AssessmentWorkflowTransitionResult(BaseModel):
    case_id: int
    profile_id: int
    previous_status: str | None
    current_status: str
    action: str
    message: str
    event: AssessmentWorkflowEventRead


class AssessmentWorkflowRule(BaseModel):
    from_status: str
    action: str
    to_status: str
    allowed_roles: list[str]
    description: str


class AssessmentWorkflowSummary(BaseModel):
    total_cases: int
    by_status: dict[str, int]
    pending_external_assessment: int
    waiting_for_clarification: int
    approved_cases: int
    rejected_cases: int
    overdue_cases: int
    rules: list[AssessmentWorkflowRule]
