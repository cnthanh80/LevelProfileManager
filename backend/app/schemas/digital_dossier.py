from datetime import datetime
from typing import Any
from pydantic import BaseModel


class ProfileVersionCreate(BaseModel):
    title: str | None = None
    change_summary: str | None = None


class ProfileVersionRead(BaseModel):
    id: int
    profile_id: int
    version_no: int
    title: str
    status: str
    snapshot_hash: str
    change_summary: str | None = None
    created_by: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProfileVersionDetail(ProfileVersionRead):
    snapshot: dict[str, Any]


class VersionCompareResult(BaseModel):
    from_version: int
    to_version: int
    changed_fields: list[str]
    added_checklist_items: int
    removed_checklist_items: int
    changed_checklist_items: int
    added_evidence_items: int
    removed_evidence_items: int
    summary: list[str]


class SignProfileRequest(BaseModel):
    signer_name: str | None = None
    signer_role: str | None = None
    sign_method: str = "MOCK"
    certificate_subject: str | None = None
    comment: str | None = None


class ProfileSignatureRead(BaseModel):
    id: int
    profile_id: int
    version_id: int
    signer_id: int | None = None
    signer_name: str
    signer_role: str | None = None
    sign_method: str
    status: str
    signature_hash: str
    certificate_subject: str | None = None
    signed_file_path: str | None = None
    comment: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DossierSummary(BaseModel):
    profile_id: int
    total_versions: int
    total_signatures: int
    latest_version_no: int | None = None
    latest_hash: str | None = None
    signed: bool
    latest_signature_status: str | None = None
