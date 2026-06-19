from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PasswordPolicyStatus(BaseModel):
    min_length: int
    require_uppercase: bool
    require_lowercase: bool
    require_digit: bool
    require_special: bool
    lockout_enabled: bool
    lockout_threshold: int
    lockout_minutes: int


class PasswordValidationRequest(BaseModel):
    password: str


class PasswordValidationResult(BaseModel):
    valid: bool
    score: int
    issues: list[str]


class SecurityEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    severity: str
    username: str | None = None
    user_id: int | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    detail: str | None = None
    created_at: datetime


class SecurityEventCreate(BaseModel):
    event_type: str
    severity: str = "INFO"
    username: str | None = None
    user_id: int | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    detail: str | None = None


class SecuritySummary(BaseModel):
    total_events: int
    failed_logins: int
    locked_accounts: int
    high_severity_events: int
    last_events: list[SecurityEventRead]
