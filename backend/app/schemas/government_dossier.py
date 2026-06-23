from datetime import datetime
from pydantic import BaseModel, Field


class GovernmentDossierGenerateRequest(BaseModel):
    include_evidence: bool = True
    notes: str | None = None


class GovernmentDossierFileRead(BaseModel):
    id: int
    dossier_id: int
    profile_id: int
    file_type: str
    display_name: str
    file_name: str
    content_type: str | None = None
    file_size: int
    checksum_sha256: str | None = None
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


class GovernmentDossierRead(BaseModel):
    id: int
    profile_id: int
    dossier_code: str
    title: str
    version: int
    status: str
    package_filename: str
    package_size: int
    checksum_sha256: str | None = None
    included_evidence_count: int
    generated_by: int | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GovernmentDossierDetail(GovernmentDossierRead):
    files: list[GovernmentDossierFileRead] = Field(default_factory=list)


class GovernmentDossierSummary(BaseModel):
    total_dossiers: int
    latest_version_by_profile: dict[str, int]
    generated_files: int
    total_package_size: int
