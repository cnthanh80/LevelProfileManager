from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.exported_document import ExportedDocument
from app.models.user import User
from app.schemas.common import Page
from app.schemas.exported_document import ExportRequest, ExportedDocumentRead
from app.services.export_service import export_profile_document

router = APIRouter()


@router.post("/profiles/{profile_id}/exports", response_model=ExportedDocumentRead, status_code=status.HTTP_201_CREATED)
def export_profile(
    profile_id: int,
    payload: ExportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REVIEWER", "APPROVER")),
):
    return export_profile_document(
        db,
        profile_id=profile_id,
        document_type=payload.document_type,
        file_format=payload.file_format,
        generated_by=current_user.id,
    )


@router.get("/exported-documents", response_model=Page[ExportedDocumentRead])
def list_exported_documents(
    db: Session = Depends(get_db),
    profile_id: int | None = Query(default=None),
    document_type: str | None = Query(default=None),
    file_format: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
):
    stmt = select(ExportedDocument)
    count_stmt = select(func.count(ExportedDocument.id))
    filters = []
    if profile_id is not None:
        filters.append(ExportedDocument.profile_id == profile_id)
    if document_type:
        filters.append(ExportedDocument.document_type == document_type.upper())
    if file_format:
        filters.append(ExportedDocument.file_format == file_format.lower())
    if filters:
        stmt = stmt.where(*filters)
        count_stmt = count_stmt.where(*filters)
    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(ExportedDocument.created_at.desc(), ExportedDocument.id.desc()).limit(limit).offset(offset)).all()
    return Page[ExportedDocumentRead](items=items, total=total, limit=limit, offset=offset)


@router.get("/exported-documents/{document_id}", response_model=ExportedDocumentRead)
def get_exported_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.get(ExportedDocument, document_id)
    if not item:
        raise HTTPException(status_code=404, detail="Exported document not found")
    return item


@router.get("/exported-documents/{document_id}/download")
def download_exported_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.get(ExportedDocument, document_id)
    if not item:
        raise HTTPException(status_code=404, detail="Exported document not found")
    path = Path(item.storage_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Physical file not found")
    return FileResponse(path=str(path), media_type=item.content_type or "application/octet-stream", filename=item.original_filename)


@router.delete("/exported-documents/{document_id}")
def delete_exported_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER")),
):
    item = db.get(ExportedDocument, document_id)
    if not item:
        raise HTTPException(status_code=404, detail="Exported document not found")
    path = Path(item.storage_path)
    db.delete(item)
    db.commit()
    if path.exists():
        path.unlink()
    return {"status": "deleted", "document_id": document_id}
