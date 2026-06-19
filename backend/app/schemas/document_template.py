from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DocumentTemplateCreate(BaseModel):
    code: str
    name: str
    document_type: str
    version: str = "1.0"
    description: str | None = None
    agency_name: str | None = None
    file_format: str = "docx"
    template_path: str | None = None
    is_active: bool = True
    sort_order: int = 100


class DocumentTemplateUpdate(BaseModel):
    name: str | None = None
    version: str | None = None
    description: str | None = None
    agency_name: str | None = None
    file_format: str | None = None
    template_path: str | None = None
    is_active: bool | None = None
    sort_order: int | None = None


class DocumentTemplateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    document_type: str
    version: str
    description: str | None = None
    agency_name: str | None = None
    file_format: str
    template_path: str | None = None
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime


class GovernmentDocumentRequest(BaseModel):
    document_type: str = "PROFILE_EXPLANATION"
    file_format: str = "docx"
    template_code: str | None = None
    agency_name: str | None = "NGÂN HÀNG CHÍNH SÁCH XÃ HỘI"
    signer_title: str | None = "THỦ TRƯỞNG ĐƠN VỊ"
    signer_name: str | None = None
    place_name: str | None = "Hà Nội"
