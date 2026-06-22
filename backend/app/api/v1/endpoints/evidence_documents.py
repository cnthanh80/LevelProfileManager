from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.evidence_document import EvidenceDocument
from app.models.user import User
from app.schemas.common import Page
from app.schemas.evidence_document import EvidenceDocumentRead, EvidenceDocumentUpdate, EvidenceDocumentUploadResponse
from app.services.evidence_service import delete_evidence, save_evidence_file, validate_profile_and_answer

router = APIRouter()


def _deduplicate_evidence(items: list[EvidenceDocument]) -> list[EvidenceDocument]:
    """Keep the newest row for identical evidence records.

    UAT scripts may upload the same sample evidence many times. The database
    can still keep historical rows, but list screens should not display the
    exact same file repeatedly.
    """
    seen: set[tuple] = set()
    result: list[EvidenceDocument] = []
    for item in items:
        key = (
            item.profile_id,
            item.checklist_answer_id,
            item.document_type,
            item.title,
            item.original_filename,
            item.checksum_sha256,
        )
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result



@router.post("/evidence-documents", response_model=EvidenceDocumentUploadResponse, status_code=status.HTTP_201_CREATED)
def upload_evidence_document(
    profile_id: int = Form(...),
    document_type: str = Form(...),
    title: str = Form(...),
    checklist_answer_id: int | None = Form(default=None),
    description: str | None = Form(default=None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "OPERATOR", "REVIEWER")),
):
    return save_evidence_file(
        db,
        profile_id=profile_id,
        checklist_answer_id=checklist_answer_id,
        document_type=document_type,
        title=title,
        description=description,
        file=file,
        uploaded_by=current_user.id,
    )


@router.get("/evidence-documents", response_model=Page[EvidenceDocumentRead])
def list_evidence_documents(
    db: Session = Depends(get_db),
    profile_id: int | None = Query(default=None),
    checklist_answer_id: int | None = Query(default=None),
    document_type: str | None = Query(default=None),
    q: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
):
    stmt = select(EvidenceDocument)
    count_stmt = select(func.count(EvidenceDocument.id))
    filters = []
    if profile_id is not None:
        filters.append(EvidenceDocument.profile_id == profile_id)
    if checklist_answer_id is not None:
        filters.append(EvidenceDocument.checklist_answer_id == checklist_answer_id)
    if document_type:
        filters.append(EvidenceDocument.document_type == document_type)
    if q:
        pattern = f"%{q}%"
        filters.append((EvidenceDocument.title.ilike(pattern)) | (EvidenceDocument.original_filename.ilike(pattern)))
    if filters:
        stmt = stmt.where(*filters)
        count_stmt = count_stmt.where(*filters)
    # Fetch then de-duplicate exact duplicate evidence rows for UAT-friendly display.
    all_items = db.scalars(stmt.order_by(EvidenceDocument.created_at.desc(), EvidenceDocument.id.desc())).all()
    unique_items = _deduplicate_evidence(all_items)
    total = len(unique_items)
    items = unique_items[offset: offset + limit]
    return Page[EvidenceDocumentRead](items=items, total=total, limit=limit, offset=offset)


@router.get("/evidence-documents/{document_id}", response_model=EvidenceDocumentRead)
def get_evidence_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.get(EvidenceDocument, document_id)
    if not item:
        raise HTTPException(status_code=404, detail="Evidence document not found")
    return item


@router.put("/evidence-documents/{document_id}", response_model=EvidenceDocumentRead)
def update_evidence_document(
    document_id: int,
    payload: EvidenceDocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "OPERATOR", "REVIEWER")),
):
    item = db.get(EvidenceDocument, document_id)
    if not item:
        raise HTTPException(status_code=404, detail="Evidence document not found")
    data = payload.model_dump(exclude_unset=True)
    if "checklist_answer_id" in data:
        validate_profile_and_answer(db, item.profile_id, data["checklist_answer_id"])
    for key, value in data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.get("/evidence-documents/{document_id}/download")
def download_evidence_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.get(EvidenceDocument, document_id)
    if not item:
        raise HTTPException(status_code=404, detail="Evidence document not found")
    path = Path(item.storage_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Physical file not found")
    return FileResponse(
        path=str(path),
        media_type=item.content_type or "application/octet-stream",
        filename=item.original_filename,
    )


@router.delete("/evidence-documents/{document_id}")
def remove_evidence_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER")),
):
    item = db.get(EvidenceDocument, document_id)
    if not item:
        raise HTTPException(status_code=404, detail="Evidence document not found")
    delete_evidence(db, item)
    return {"status": "deleted", "document_id": document_id}


@router.get("/profiles/{profile_id}/evidence-documents", response_model=list[EvidenceDocumentRead])
def list_profile_evidence_documents(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = db.scalars(
        select(EvidenceDocument).where(EvidenceDocument.profile_id == profile_id).order_by(EvidenceDocument.created_at.desc(), EvidenceDocument.id.desc())
    ).all()
    return _deduplicate_evidence(items)


@router.get("/checklist-answers/{answer_id}/evidence-documents", response_model=list[EvidenceDocumentRead])
def list_answer_evidence_documents(
    answer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = db.scalars(
        select(EvidenceDocument).where(EvidenceDocument.checklist_answer_id == answer_id).order_by(EvidenceDocument.created_at.desc(), EvidenceDocument.id.desc())
    ).all()
    return _deduplicate_evidence(items)
