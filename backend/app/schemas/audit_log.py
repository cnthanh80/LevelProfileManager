from datetime import datetime
from pydantic import BaseModel, ConfigDict


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
    created_at: datetime
    updated_at: datetime
