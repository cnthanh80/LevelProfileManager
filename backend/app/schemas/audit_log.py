from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor_id: int | None = None
    action: str
    entity_type: str
    entity_id: int | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    detail: str | None = None
    request_id: str | None = None
    http_method: str | None = None
    path: str | None = None
    status_code: int | None = None
    duration_ms: int | None = None
    success: bool | None = None
    source: str | None = None
    created_at: datetime
    updated_at: datetime


class AuditLogCreate(BaseModel):
    action: str = Field(min_length=2, max_length=150)
    entity_type: str = Field(min_length=2, max_length=150)
    entity_id: int | None = None
    detail: str | None = None
    source: str = "MANUAL"


class AuditLogSummary(BaseModel):
    total: int
    success: int
    failed: int
    by_action: dict[str, int]
    by_entity_type: dict[str, int]
    by_http_method: dict[str, int]
    by_status_code: dict[str, int]


class AuditActionItem(BaseModel):
    action: str
    count: int
