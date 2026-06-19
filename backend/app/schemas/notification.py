from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class NotificationCreate(BaseModel):
    event_type: str = "MANUAL_TEST"
    channel: str = "IN_APP"
    recipient: str = "admin@example.com"
    subject: str = "Thông báo kiểm thử"
    message: str = "Nội dung thông báo kiểm thử"
    related_profile_id: int | None = None


class ProfileReminderCreate(BaseModel):
    channel: str = "IN_APP"
    recipient: str = "attt@example.com"
    subject: str | None = None
    message: str | None = None


class BulkReminderRequest(BaseModel):
    channel: str = "IN_APP"
    recipient: str = "attt@example.com"
    days: int = Field(default=30, ge=1, le=365)


class NotificationLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    channel: str
    recipient: str
    subject: str
    message: str
    status: str
    related_profile_id: int | None = None
    error_message: str | None = None
    sent_at: datetime | None = None
    created_by: int | None = None
    created_at: datetime
    updated_at: datetime


class NotificationSummary(BaseModel):
    total: int
    pending: int
    sent: int
    failed: int
    by_channel: dict[str, int] = Field(default_factory=dict)
    by_event_type: dict[str, int] = Field(default_factory=dict)


class NotificationRuntimeStatus(BaseModel):
    dry_run: bool
    channels: dict
