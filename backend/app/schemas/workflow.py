from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class WorkflowState(BaseModel):
    profile_id: int
    profile_code: str
    current_status: str
    allowed_actions: list[str]


class WorkflowTransitionRequest(BaseModel):
    action: str = Field(min_length=3, max_length=100)
    comment: str | None = Field(default=None, max_length=4000)


class WorkflowTransitionResponse(BaseModel):
    profile_id: int
    from_status: str
    to_status: str
    action: str
    comment: str | None = None


class WorkflowHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    profile_id: int
    from_status: str | None = None
    to_status: str
    action: str
    comment: str | None = None
    actor_user_id: int | None = None
    created_at: datetime


class ApprovalCommentCreate(BaseModel):
    workflow_state: str | None = Field(default=None, max_length=80)
    action: str = Field(default="comment", max_length=100)
    comment: str = Field(min_length=1, max_length=4000)


class ApprovalCommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    profile_id: int
    workflow_state: str
    action: str
    comment: str
    created_by: int | None = None
    created_at: datetime


class WorkflowSummaryItem(BaseModel):
    status: str
    total: int


class WorkflowSummary(BaseModel):
    total: int
    items: list[WorkflowSummaryItem]
