from datetime import datetime
from pydantic import BaseModel, Field


class EnterpriseConfigurationRead(BaseModel):
    id: int
    config_key: str
    config_group: str
    display_name: str
    config_value: str | None = None
    value_type: str
    is_secret: bool
    is_enabled: bool
    description: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EnterpriseConfigurationUpsert(BaseModel):
    config_key: str = Field(min_length=2, max_length=120)
    config_group: str = Field(default="GENERAL", max_length=80)
    display_name: str = Field(min_length=2, max_length=255)
    config_value: str | None = None
    value_type: str = "STRING"
    is_secret: bool = False
    is_enabled: bool = True
    description: str | None = None


class EnterpriseHealthCheckRead(BaseModel):
    id: int
    component_code: str
    component_name: str
    component_group: str
    status: str
    latency_ms: int | None = None
    message: str | None = None
    checked_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class EnterpriseJobScheduleRead(BaseModel):
    id: int
    job_code: str
    job_name: str
    job_group: str
    schedule_expression: str
    is_enabled: bool
    last_run_at: datetime | None = None
    next_run_hint: str | None = None
    last_status: str | None = None
    last_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EnterpriseJobScheduleUpsert(BaseModel):
    job_code: str = Field(min_length=2, max_length=120)
    job_name: str = Field(min_length=2, max_length=255)
    job_group: str = Field(default="GENERAL", max_length=80)
    schedule_expression: str = Field(default="DAILY 00:30", max_length=120)
    is_enabled: bool = True
    next_run_hint: str | None = None


class DataRetentionPolicyRead(BaseModel):
    id: int
    policy_code: str
    data_domain: str
    retention_days: int
    archive_enabled: bool
    purge_enabled: bool
    legal_hold: bool
    description: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DataRetentionPolicyUpsert(BaseModel):
    policy_code: str = Field(min_length=2, max_length=120)
    data_domain: str = Field(min_length=2, max_length=120)
    retention_days: int = Field(default=365, ge=1)
    archive_enabled: bool = False
    purge_enabled: bool = False
    legal_hold: bool = False
    description: str | None = None


class BackupRecordRead(BaseModel):
    id: int
    backup_code: str
    backup_type: str
    scope: str
    status: str
    storage_location: str | None = None
    checksum: str | None = None
    size_mb: int
    started_at: datetime
    completed_at: datetime | None = None
    validated_at: datetime | None = None
    validation_status: str | None = None
    notes: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class BackupRecordCreate(BaseModel):
    backup_type: str = "LOGICAL"
    scope: str = "DATABASE"
    status: str = "COMPLETED"
    storage_location: str | None = None
    size_mb: int = Field(default=0, ge=0)
    notes: str | None = None


class EnterpriseReadinessCheck(BaseModel):
    domain: str
    status: str
    score: int
    message: str


class EnterpriseReadinessDashboard(BaseModel):
    overall_score: int
    readiness_level: str
    checks: list[EnterpriseReadinessCheck]
    recommendations: list[str]


class EnterpriseHealthDashboard(BaseModel):
    status: str
    generated_at: datetime
    components: list[EnterpriseHealthCheckRead]
    summary: dict[str, int]


class EnterpriseCenterDashboard(BaseModel):
    readiness: EnterpriseReadinessDashboard
    health: EnterpriseHealthDashboard
    configuration_count: int
    enabled_job_count: int
    retention_policy_count: int
    latest_backup: BackupRecordRead | None = None
