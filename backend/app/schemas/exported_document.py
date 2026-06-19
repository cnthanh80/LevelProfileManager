from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ExportRequest(BaseModel):
    document_type: str = "PROFILE_EXPLANATION"
    file_format: str = "docx"


class ExportedDocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    profile_id: int
    document_type: str
    file_format: str
    title: str
    original_filename: str
    stored_filename: str
    content_type: str | None = None
    file_size: int
    checksum_sha256: str
    generated_by: int | None = None
    created_at: datetime
    updated_at: datetime
