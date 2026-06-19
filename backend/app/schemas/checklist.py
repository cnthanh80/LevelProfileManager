from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.security_requirement import SecurityRequirementRead


class ChecklistAnswerBase(BaseModel):
    status: str = Field(default="NON_COMPLIANT", description="COMPLIANT/NON_COMPLIANT/NOT_APPLICABLE")
    current_state: str | None = None
    improvement_plan: str | None = None
    evidence_note: str | None = None
    evidence_count: int = Field(default=0, ge=0)
    owner: str | None = None
    due_date: date | None = None


class ChecklistAnswerUpdate(BaseModel):
    status: str | None = Field(default=None, description="COMPLIANT/NON_COMPLIANT/NOT_APPLICABLE")
    current_state: str | None = None
    improvement_plan: str | None = None
    evidence_note: str | None = None
    evidence_count: int | None = Field(default=None, ge=0)
    owner: str | None = None
    due_date: date | None = None


class ChecklistAnswerRead(ChecklistAnswerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    profile_id: int
    requirement_id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ChecklistItemRead(ChecklistAnswerRead):
    requirement: SecurityRequirementRead


class ChecklistGenerateResponse(BaseModel):
    profile_id: int
    proposed_level: int
    created: int
    existing: int
    total: int


class ComplianceGroupSummary(BaseModel):
    total: int
    compliant: int
    non_compliant: int
    not_applicable: int
    mandatory_total: int
    mandatory_non_compliant: int
    compliance_percent: float


class ComplianceSummary(BaseModel):
    profile_id: int
    proposed_level: int
    total: int
    compliant: int
    non_compliant: int
    not_applicable: int
    mandatory_total: int
    mandatory_non_compliant: int
    overall_percent: float
    by_group: dict[str, ComplianceGroupSummary]
    warnings: list[str]
