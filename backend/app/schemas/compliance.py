from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ClassificationInput(BaseModel):
    has_personal_data: bool = False
    has_financial_data: bool = False
    has_sensitive_data: bool = False
    has_state_secret_or_highly_sensitive_data: bool = False
    internet_exposed: bool = False
    third_party_connections: bool = False
    cross_org_connections: bool = False
    user_count: int = Field(default=0, ge=0)
    transaction_per_day: int = Field(default=0, ge=0)
    downtime_impact: str = "LOW"  # LOW/MEDIUM/HIGH/CRITICAL
    confidentiality_impact: str = "LOW"
    integrity_impact: str = "LOW"
    availability_impact: str = "LOW"


class ClassificationResult(BaseModel):
    suggested_level: int
    confidence_score: int
    reasons: list[str]


class GapItem(BaseModel):
    requirement_id: int
    code: str
    title: str
    group_name: str
    category: str
    is_mandatory: bool
    status: str | None = None


class GapAnalysisResult(BaseModel):
    profile_id: int
    proposed_level: int
    total_requirements: int
    compliant_count: int
    non_compliant_count: int
    not_applicable_count: int
    missing_answer_count: int
    mandatory_gap_count: int
    gaps: list[GapItem]


class ComplianceScoreResult(BaseModel):
    profile_id: int
    management_score: int
    technical_score: int
    overall_score: int
    mandatory_total: int
    mandatory_compliant: int
    gap_total: int


class RiskAssessmentResult(BaseModel):
    profile_id: int
    risk_score: int
    risk_level: str
    risk_factors: list[str]
    recommendation: str


class ReadinessResult(BaseModel):
    profile_id: int
    readiness_score: int
    readiness_status: str
    is_ready_for_assessment: bool
    blockers: list[str]


class ProfileAssessmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    profile_id: int
    suggested_level: int
    current_level: int
    confidence_score: int
    classification_reasons: str | None
    missing_requirements: str | None
    readiness_status: str
    readiness_score: int
    is_ready_for_assessment: bool
    assessed_by: int | None
    created_at: datetime
    updated_at: datetime
