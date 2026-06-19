import hashlib
import os
import re
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.evidence_document import EvidenceDocument
from app.models.level_profile import LevelProfile
from app.models.profile_requirement_answer import ProfileRequirementAnswer

ALLOWED_EXTENSIONS = {".doc", ".docx", ".xls", ".xlsx", ".pdf", ".png", ".jpg", ".jpeg"}
MAX_UPLOAD_SIZE = 50 * 1024 * 1024


def _safe_filename(filename: str) -> str:
    name = os.path.basename(filename or "evidence.bin")
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
    return name or "evidence.bin"


def _storage_root() -> Path:
    root = Path(settings.FILE_STORAGE_PATH)
    root.mkdir(parents=True, exist_ok=True)
    return root


def _sync_answer_evidence_count(db: Session, answer_id: int | None) -> None:
    if not answer_id:
        return
    count = db.scalar(select(func.count(EvidenceDocument.id)).where(EvidenceDocument.checklist_answer_id == answer_id)) or 0
    answer = db.get(ProfileRequirementAnswer, answer_id)
    if answer:
        answer.evidence_count = int(count)


def validate_profile_and_answer(db: Session, profile_id: int, checklist_answer_id: int | None) -> None:
    if db.get(LevelProfile, profile_id) is None:
        raise HTTPException(status_code=404, detail="Level profile not found")
    if checklist_answer_id is not None:
        answer = db.get(ProfileRequirementAnswer, checklist_answer_id)
        if not answer:
            raise HTTPException(status_code=404, detail="Checklist answer not found")
        if answer.profile_id != profile_id:
            raise HTTPException(status_code=400, detail="Checklist answer does not belong to this profile")


def save_evidence_file(
    db: Session,
    *,
    profile_id: int,
    checklist_answer_id: int | None,
    document_type: str,
    title: str,
    description: str | None,
    file: UploadFile,
    uploaded_by: int | None,
) -> EvidenceDocument:
    validate_profile_and_answer(db, profile_id, checklist_answer_id)

    original_name = _safe_filename(file.filename or "evidence.bin")
    ext = Path(original_name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    profile_dir = _storage_root() / f"profile_{profile_id}"
    profile_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}{ext}"
    storage_path = profile_dir / stored_name

    sha256 = hashlib.sha256()
    size = 0
    with storage_path.open("wb") as out:
        while True:
            chunk = file.file.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > MAX_UPLOAD_SIZE:
                out.close()
                storage_path.unlink(missing_ok=True)
                raise HTTPException(status_code=400, detail="File is too large. Max size is 50MB")
            sha256.update(chunk)
            out.write(chunk)

    existing_versions = db.scalar(
        select(func.count(EvidenceDocument.id)).where(
            EvidenceDocument.profile_id == profile_id,
            EvidenceDocument.document_type == document_type,
            EvidenceDocument.original_filename == original_name,
        )
    ) or 0

    item = EvidenceDocument(
        profile_id=profile_id,
        checklist_answer_id=checklist_answer_id,
        document_type=document_type,
        title=title,
        description=description,
        original_filename=original_name,
        stored_filename=stored_name,
        storage_path=str(storage_path),
        content_type=file.content_type,
        file_size=size,
        checksum_sha256=sha256.hexdigest(),
        version=int(existing_versions) + 1,
        uploaded_by=uploaded_by,
    )
    db.add(item)
    _sync_answer_evidence_count(db, checklist_answer_id)
    db.commit()
    db.refresh(item)
    return item


def delete_evidence(db: Session, item: EvidenceDocument) -> None:
    answer_id = item.checklist_answer_id
    try:
        Path(item.storage_path).unlink(missing_ok=True)
    except Exception:
        pass
    db.delete(item)
    db.flush()
    _sync_answer_evidence_count(db, answer_id)
    db.commit()
