from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class AiClassificationInput(BaseModel):
    system_name: str | None = None
    system_purpose: str | None = None
    data_description: str | None = None
    user_groups: str | None = None
    deployment_model: str | None = None
    internet_exposed: bool = False
    third_party_connections: bool = False
    cross_org_connections: bool = False
    has_personal_data: bool = False
    has_financial_data: bool = False
    has_sensitive_data: bool = False
    has_state_secret_or_highly_sensitive_data: bool = False
    user_count: int = Field(default=0, ge=0)
    transaction_per_day: int = Field(default=0, ge=0)
    confidentiality_impact: str = "MEDIUM"
    integrity_impact: str = "MEDIUM"
    availability_impact: str = "MEDIUM"
    business_criticality: str = "MEDIUM"


class AiRecommendationResult(BaseModel):
    profile_id: int | None = None
    information_system_id: int | None = None
    current_level: int | None = None
    recommended_level: int
    confidence_score: int
    risk_score: int
    risk_band: str
    mismatch_status: str
    reasons: list[str]
    evidence: list[str]
    explanation: str
    recommended_actions: list[str]


class AiLevelRecommendationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    profile_id: int
    information_system_id: int | None
    current_level: int | None
    recommended_level: int
    confidence_score: int
    risk_score: int
    risk_band: str
    mismatch_status: str
    input_summary: str | None
    reasons_json: str | None
    evidence_json: str | None
    explanation: str | None
    recommended_actions_json: str | None
    created_by: int | None
    created_at: datetime
    updated_at: datetime
