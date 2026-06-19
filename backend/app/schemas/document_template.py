from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DocumentTemplateCreate(BaseModel):
    code: str
    name: str
    document_type: str
    category: str = "GOVERNMENT"
    version: str = "1.0"
    description: str | None = None
    agency_name: str | None = None
    official_number_prefix: str | None = None
    variable_schema: str | None = None
    file_format: str = "docx"
    template_path: str | None = None
    checksum_sha256: str | None = None
    is_active: bool = True
    is_default: bool = False
    sort_order: int = 100


class DocumentTemplateUpdate(BaseModel):
    name: str | None = None
    document_type: str | None = None
    category: str | None = None
    version: str | None = None
    description: str | None = None
    agency_name: str | None = None
    official_number_prefix: str | None = None
    variable_schema: str | None = None
    file_format: str | None = None
    template_path: str | None = None
    checksum_sha256: str | None = None
    is_active: bool | None = None
    is_default: bool | None = None
    sort_order: int | None = None


class DocumentTemplateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    document_type: str
    category: str = "GENERAL"
    version: str
    description: str | None = None
    agency_name: str | None = None
    official_number_prefix: str | None = None
    variable_schema: str | None = None
    file_format: str
    template_path: str | None = None
    checksum_sha256: str | None = None
    is_active: bool
    is_default: bool = False
    sort_order: int
    uploaded_by: int | None = None
    uploaded_at: datetime | None = None
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


class TemplateCenterSummary(BaseModel):
    total_templates: int
    active_templates: int
    uploaded_templates: int
    default_templates: int
    by_document_type: dict[str, int]
    by_category: dict[str, int]


class TemplateVariableItem(BaseModel):
    key: str
    description: str
    sample: str | None = None


class TemplatePreviewRequest(BaseModel):
    profile_id: int
    template_code: str | None = None
    document_type: str = "PROFILE_EXPLANATION"
