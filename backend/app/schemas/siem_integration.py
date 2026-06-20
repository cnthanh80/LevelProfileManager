from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class SiemConnectorBase(BaseModel):
    connector_code: str
    connector_name: str
    connector_type: str = "SYSLOG"
    endpoint_url: str | None = None
    auth_type: str | None = "NONE"
    is_enabled: bool = True
    description: str | None = None


class SiemConnectorCreate(SiemConnectorBase):
    pass


class SiemConnectorUpdate(BaseModel):
    connector_name: str | None = None
    connector_type: str | None = None
    endpoint_url: str | None = None
    auth_type: str | None = None
    is_enabled: bool | None = None
    description: str | None = None


class SiemConnectorRead(SiemConnectorBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    last_sync_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class SiemEventBase(BaseModel):
    connector_id: int | None = None
    source_system: str | None = None
    event_type: str
    severity: str = "INFO"
    status: str = "OPEN"
    username: str | None = None
    ip_address: str | None = None
    asset_code: str | None = None
    information_system_id: int | None = None
    profile_id: int | None = None
    correlation_key: str | None = None
    raw_message: str | None = None
    normalized_message: str | None = None


class SiemEventIngest(SiemEventBase):
    pass


class SiemEventRead(SiemEventBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


class SiemRuleBase(BaseModel):
    rule_code: str
    rule_name: str
    event_type: str | None = None
    min_severity: str = "MEDIUM"
    threshold_count: int = Field(default=5, ge=1)
    window_minutes: int = Field(default=15, ge=1)
    risk_score: int = Field(default=50, ge=0, le=100)
    action_hint: str | None = None
    is_enabled: bool = True


class SiemRuleCreate(SiemRuleBase):
    pass


class SiemRuleRead(SiemRuleBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


class SiemDashboard(BaseModel):
    total_connectors: int
    enabled_connectors: int
    total_events: int
    open_events: int
    critical_events: int
    high_events: int
    by_severity: dict
    by_event_type: dict
    top_source_systems: list[dict]
    risk_score: int
    recommendations: list[str]


class SiemStatus(BaseModel):
    status: str
    version: str
    supported_integrations: list[str]
    enabled_connectors: int
    message: str
