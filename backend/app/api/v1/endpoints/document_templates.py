from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.document_template import DocumentTemplate
from app.models.user import User
from app.schemas.common import Page
from app.schemas.document_template import DocumentTemplateCreate, DocumentTemplateRead, DocumentTemplateUpdate, GovernmentDocumentRequest
from app.schemas.exported_document import ExportedDocumentRead
from app.services.template_engine import GOVERNMENT_DOCUMENT_TYPES, generate_government_document, seed_default_templates

router = APIRouter()


@router.get("/document-templates", response_model=Page[DocumentTemplateRead])
def list_document_templates(
    db: Session = Depends(get_db),
    document_type: str | None = Query(default=None),
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
    item = DocumentTemplate(**payload.model_dump())
    item.document_type = item.document_type.upper()
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/document-templates/{template_id}", response_model=DocumentTemplateRead)
def get_document_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.get(DocumentTemplate, template_id)
    if not item:
        raise HTTPException(status_code=404, detail="Document template not found")
    return item


@router.put("/document-templates/{template_id}", response_model=DocumentTemplateRead)
def update_document_template(
    template_id: int,
    payload: DocumentTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER")),
):
    item = db.get(DocumentTemplate, template_id)
    if not item:
        raise HTTPException(status_code=404, detail="Document template not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value.upper() if key == "document_type" and isinstance(value, str) else value)
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
