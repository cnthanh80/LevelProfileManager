from __future__ import annotations

import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.document_template import DocumentTemplate
from app.models.information_system import InformationSystem
from app.models.level_profile import LevelProfile
from app.models.user import User
from app.schemas.common import Page
from app.schemas.document_template import (
    DocumentTemplateCreate,
    DocumentTemplateRead,
    DocumentTemplateUpdate,
    GovernmentDocumentRequest,
    TemplateCenterSummary,
    TemplatePreviewRequest,
)
from app.schemas.exported_document import ExportedDocumentRead
from app.services.template_engine import GOVERNMENT_DOCUMENT_TYPES, generate_government_document, seed_default_templates

router = APIRouter()
TEMPLATE_ROOT = Path("/app/storage/templates")
ALLOWED_EXTENSIONS = {".docx", ".pdf", ".xlsx", ".html", ".txt"}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _template_or_404(db: Session, template_id: int) -> DocumentTemplate:
    item = db.get(DocumentTemplate, template_id)
    if not item:
        raise HTTPException(status_code=404, detail="Document template not found")
    return item


@router.get("/document-templates/center/summary", response_model=TemplateCenterSummary)
def template_center_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = db.scalars(select(DocumentTemplate)).all()
    by_type: dict[str, int] = {}
    by_category: dict[str, int] = {}
    for item in items:
        by_type[item.document_type] = by_type.get(item.document_type, 0) + 1
        by_category[item.category or "GENERAL"] = by_category.get(item.category or "GENERAL", 0) + 1
    return TemplateCenterSummary(
        total_templates=len(items),
        active_templates=sum(1 for x in items if x.is_active),
        uploaded_templates=sum(1 for x in items if x.template_path),
        default_templates=sum(1 for x in items if getattr(x, "is_default", False)),
        by_document_type=by_type,
        by_category=by_category,
    )


@router.get("/document-templates/variables")
def list_template_variables(current_user: User = Depends(get_current_user)):
    return {
        "variables": [
            {"key": "agency_name", "description": "Tên cơ quan, tổ chức", "sample": "NGÂN HÀNG CHÍNH SÁCH XÃ HỘI"},
            {"key": "place_name", "description": "Địa danh ban hành văn bản", "sample": "Hà Nội"},
            {"key": "document_date", "description": "Ngày sinh văn bản", "sample": "20/06/2026"},
            {"key": "profile.profile_code", "description": "Mã hồ sơ đề xuất cấp độ", "sample": "HS-CD-CORE-2026"},
            {"key": "profile.proposed_level", "description": "Cấp độ đề xuất", "sample": "3"},
            {"key": "profile.status", "description": "Trạng thái hồ sơ", "sample": "INTERNALLY_APPROVED"},
            {"key": "system.code", "description": "Mã hệ thống thông tin", "sample": "CORE"},
            {"key": "system.name", "description": "Tên hệ thống thông tin", "sample": "Core Banking"},
            {"key": "system.deployment_model", "description": "Mô hình triển khai", "sample": "on_premise"},
            {"key": "signer_title", "description": "Chức danh người ký", "sample": "GIÁM ĐỐC"},
            {"key": "signer_name", "description": "Họ tên người ký", "sample": "Nguyễn Văn A"},
        ]
    }


@router.post("/document-templates/preview-context")
def preview_template_context(
    payload: TemplatePreviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = db.get(LevelProfile, payload.profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Level profile not found")
    system = db.get(InformationSystem, profile.information_system_id)
    template = None
    if payload.template_code:
        template = db.scalar(select(DocumentTemplate).where(DocumentTemplate.code == payload.template_code))
    return {
        "template": {
            "code": template.code if template else payload.template_code,
            "document_type": template.document_type if template else payload.document_type,
            "agency_name": template.agency_name if template else None,
        },
        "profile": {
            "id": profile.id,
            "profile_code": profile.profile_code,
            "name": profile.profile_code,
            "proposed_level": profile.proposed_level,
            "status": profile.status,
        },
        "system": {
            "id": system.id if system else None,
            "code": system.code if system else None,
            "name": system.name if system else None,
            "deployment_model": system.deployment_model if system else None,
            "environment": system.environment if system else None,
        },
        "document": {
            "document_type": payload.document_type,
            "document_date": datetime.utcnow().strftime("%d/%m/%Y"),
        },
    }


@router.get("/document-templates", response_model=Page[DocumentTemplateRead])
def list_document_templates(
    db: Session = Depends(get_db),
    document_type: str | None = Query(default=None),
    category: str | None = Query(default=None),
    active_only: bool = Query(default=True),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
):
    stmt = select(DocumentTemplate)
    count_stmt = select(func.count(DocumentTemplate.id))
    filters = []
    if document_type:
        filters.append(DocumentTemplate.document_type == document_type.upper())
    if category:
        filters.append(DocumentTemplate.category == category.upper())
    if active_only:
        filters.append(DocumentTemplate.is_active == True)
    if filters:
        stmt = stmt.where(*filters)
        count_stmt = count_stmt.where(*filters)
    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(DocumentTemplate.sort_order, DocumentTemplate.code).limit(limit).offset(offset)).all()
    return Page[DocumentTemplateRead](items=items, total=total, limit=limit, offset=offset)


@router.post("/document-templates", response_model=DocumentTemplateRead, status_code=status.HTTP_201_CREATED)
def create_document_template(
    payload: DocumentTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER")),
):
    existing = db.scalar(select(DocumentTemplate).where(DocumentTemplate.code == payload.code))
    if existing:
        raise HTTPException(status_code=409, detail="Document template code already exists")
    data = payload.model_dump()
    data["document_type"] = data["document_type"].upper()
    data["category"] = data.get("category", "GOVERNMENT").upper()
    item = DocumentTemplate(**data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.post("/document-templates/seed-defaults")
def seed_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    created = seed_default_templates(db)
    return {"status": "ok", "created": created}


@router.get("/government-documents/types")
def list_government_document_types(current_user: User = Depends(get_current_user)):
    return [{"code": code, "title": title} for code, title in GOVERNMENT_DOCUMENT_TYPES.items()]


@router.get("/document-templates/{template_id}", response_model=DocumentTemplateRead)
def get_document_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _template_or_404(db, template_id)


@router.put("/document-templates/{template_id}", response_model=DocumentTemplateRead)
def update_document_template(
    template_id: int,
    payload: DocumentTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER")),
):
    item = _template_or_404(db, template_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        if key in {"document_type", "category"} and isinstance(value, str):
            value = value.upper()
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.post("/document-templates/{template_id}/upload", response_model=DocumentTemplateRead)
def upload_template_file(
    template_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER")),
):
    item = _template_or_404(db, template_id)
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported template file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}")
    TEMPLATE_ROOT.mkdir(parents=True, exist_ok=True)
    stored = TEMPLATE_ROOT / f"template_{template_id}_{uuid4().hex}{suffix}"
    with stored.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    item.template_path = str(stored)
    item.file_format = suffix.lstrip(".")
    item.checksum_sha256 = _sha256(stored)
    item.uploaded_by = current_user.id
    item.uploaded_at = datetime.utcnow()
    db.commit()
    db.refresh(item)
    return item


@router.get("/document-templates/{template_id}/download")
def download_template_file(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = _template_or_404(db, template_id)
    if not item.template_path or not Path(item.template_path).exists():
        raise HTTPException(status_code=404, detail="Template file not found")
    return FileResponse(path=item.template_path, filename=f"{item.code}.{item.file_format}")


@router.post("/document-templates/{template_id}/activate", response_model=DocumentTemplateRead)
def activate_template(
    template_id: int,
    make_default: bool = Query(default=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER")),
):
    item = _template_or_404(db, template_id)
    item.is_active = True
    if make_default:
        same_type = db.scalars(select(DocumentTemplate).where(DocumentTemplate.document_type == item.document_type)).all()
        for tpl in same_type:
            tpl.is_default = False
        item.is_default = True
    db.commit()
    db.refresh(item)
    return item


@router.post("/document-templates/{template_id}/deactivate", response_model=DocumentTemplateRead)
def deactivate_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER")),
):
    item = _template_or_404(db, template_id)
    item.is_active = False
    item.is_default = False
    db.commit()
    db.refresh(item)
    return item


@router.post("/profiles/{profile_id}/government-documents/generate", response_model=ExportedDocumentRead, status_code=status.HTTP_201_CREATED)
def generate_profile_government_document(
    profile_id: int,
    payload: GovernmentDocumentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REVIEWER", "APPROVER")),
):
    return generate_government_document(
        db=db,
        profile_id=profile_id,
        document_type=payload.document_type,
        file_format=payload.file_format,
        generated_by=current_user.id,
        agency_name=payload.agency_name,
        signer_title=payload.signer_title,
        signer_name=payload.signer_name,
        place_name=payload.place_name,
        template_code=payload.template_code,
    )
