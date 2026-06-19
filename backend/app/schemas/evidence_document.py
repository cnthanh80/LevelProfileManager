from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class EvidenceDocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    profile_id: int
    checklist_answer_id: int | None = None
    document_type: str
    title: str
    description: str | None = None
    original_filename: str
    stored_filename: str
    content_type: str | None = None
    file_size: int
    checksum_sha256: str
    version: int
    uploaded_by: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class EvidenceDocumentUpdate(BaseModel):
    document_type: str | None = Field(default=None, min_length=2, max_length=100)
    title: str | None = Field(default=None, min_length=3, max_length=500)
    description: str | None = None
    checklist_answer_id: int | None = None


class EvidenceDocumentUploadResponse(EvidenceDocumentRead):
    pass
