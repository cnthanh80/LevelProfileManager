from datetime import datetime
from pydantic import BaseModel, Field


class ComplianceAutomationRuleCreate(BaseModel):
    rule_code: str = Field(min_length=2, max_length=100)
    rule_name: str
    rule_type: str
    severity: str = "MEDIUM"
    threshold_value: int = 1
    is_enabled: bool = True
    description: str | None = None
    recommendation_template: str | None = None


class ComplianceAutomationRuleRead(ComplianceAutomationRuleCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ComplianceRunRequest(BaseModel):
    profile_id: int | None = None
    scope: str = "ALL_PROFILES"


# Backward-compatible schema name used by the v3.7 endpoint module.
class ComplianceAutomationRunRequest(ComplianceRunRequest):
    pass


class ComplianceAutomationRunRead(BaseModel):
    id: int
    run_code: str
    scope: str
    profile_id: int | None = None
    status: str
    total_profiles: int
    total_findings: int
    high_findings: int
    critical_findings: int
    readiness_score: int
    executive_summary: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ComplianceFindingRead(BaseModel):
    id: int
    run_id: int
    profile_id: int | None = None
    rule_code: str
    finding_type: str
    severity: str
    title: str
    description: str | None = None
    recommendation: str | None = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}




# Backward-compatible schema name used by the v3.7 endpoint module.
# The model fields are intentionally identical to ComplianceFindingRead.
class ComplianceAutomationFindingRead(ComplianceFindingRead):
    pass


class ComplianceAutomationDashboard(BaseModel):
    total_rules: int
    enabled_rules: int
    total_runs: int
    open_findings: int
    high_findings: int
    critical_findings: int
    last_run: ComplianceAutomationRunRead | None = None
    recommendations: list[str]


class ComplianceAutomationRunResult(BaseModel):
    run: ComplianceAutomationRunRead
    findings: list[ComplianceFindingRead]
