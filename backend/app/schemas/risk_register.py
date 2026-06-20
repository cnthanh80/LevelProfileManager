from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field


class RiskRegisterCreate(BaseModel):
    profile_id: int | None = None
    information_system_id: int | None = None
    risk_code: str
    title: str
    description: str | None = None
    category: str = "GENERAL"
    likelihood: int = Field(default=1, ge=1, le=5)
    impact: int = Field(default=1, ge=1, le=5)
    owner: str | None = None
    due_date: date | None = None
    mitigation_plan: str | None = None


class RiskRegisterUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    category: str | None = None
    likelihood: int | None = Field(default=None, ge=1, le=5)
    impact: int | None = Field(default=None, ge=1, le=5)
    status: str | None = None
    owner: str | None = None
    due_date: date | None = None
    mitigation_plan: str | None = None
    residual_score: int | None = Field(default=None, ge=0, le=25)


class RiskRegisterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    profile_id: int | None = None
    information_system_id: int | None = None
    risk_code: str
    title: str
    description: str | None = None
    category: str
    likelihood: int
    impact: int
    risk_score: int
    risk_level: str
    status: str
    owner: str | None = None
    due_date: date | None = None
    mitigation_plan: str | None = None
    residual_score: int | None = None
    created_by: int | None = None
    created_at: datetime
    updated_at: datetime


class RiskRegisterSummary(BaseModel):
    total: int
    open_items: int
    critical_items: int
    high_items: int
    overdue_items: int
    by_level: dict[str, int]
    by_status: dict[str, int]
    top_risks: list[RiskRegisterRead]


class SlaPolicyCreate(BaseModel):
    code: str
    name: str
    target_type: str = "WORKFLOW"
    workflow_status: str | None = None
    severity: str = "MEDIUM"
    due_hours: int = Field(default=72, ge=1, le=8760)
    warning_hours: int = Field(default=24, ge=0, le=8760)
    is_active: str = "Y"
    description: str | None = None


class SlaPolicyUpdate(BaseModel):
    name: str | None = None
    target_type: str | None = None
    workflow_status: str | None = None
    severity: str | None = None
    due_hours: int | None = Field(default=None, ge=1, le=8760)
    warning_hours: int | None = Field(default=None, ge=0, le=8760)
    is_active: str | None = None
    description: str | None = None


class SlaPolicyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    target_type: str
    workflow_status: str | None = None
    severity: str
    due_hours: int
    warning_hours: int
    is_active: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class SlaBreachItem(BaseModel):
    profile_id: int
    profile_code: str
    current_status: str
    age_hours: int
    due_hours: int
    severity: str
    state: str


class SlaSummary(BaseModel):
    active_policies: int
    warning_items: int
    breached_items: int
    items: list[SlaBreachItem]
