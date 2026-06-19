from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.profile_signature import ProfileSignature
from app.models.profile_version import ProfileVersion
from app.models.user import User
from app.schemas.common import Page
from app.schemas.digital_dossier import (
    DossierSummary,
    ProfileSignatureRead,
    ProfileVersionCreate,
    ProfileVersionDetail,
    ProfileVersionRead,
    SignProfileRequest,
    VersionCompareResult,
)
from app.services.digital_dossier_service import compare_versions, create_profile_version, dossier_summary, get_version_detail, sign_profile_version

router = APIRouter()


@router.get("/profiles/{profile_id}/dossier/summary", response_model=DossierSummary)
def get_profile_dossier_summary(profile_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return dossier_summary(db, profile_id)


@router.post("/profiles/{profile_id}/versions", response_model=ProfileVersionRead, status_code=status.HTTP_201_CREATED)
def create_version(
    profile_id: int,
    payload: ProfileVersionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REVIEWER", "APPROVER")),
):
    return create_profile_version(db, profile_id, payload.title, payload.change_summary, current_user.id)


@router.get("/profiles/{profile_id}/versions", response_model=Page[ProfileVersionRead])
def list_profile_versions(
    profile_id: int,
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
):
    total = db.scalar(select(func.count(ProfileVersion.id)).where(ProfileVersion.profile_id == profile_id)) or 0
    items = db.scalars(
        select(ProfileVersion).where(ProfileVersion.profile_id == profile_id).order_by(ProfileVersion.version_no.desc()).limit(limit).offset(offset)
    ).all()
    return Page[ProfileVersionRead](items=items, total=total, limit=limit, offset=offset)


@router.get("/profile-versions/compare", response_model=VersionCompareResult)
def compare_profile_versions(
    from_version_id: int,
    to_version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return compare_versions(db, from_version_id, to_version_id)


@router.get("/profile-versions/{version_id}", response_model=ProfileVersionDetail)
def get_profile_version(version_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.get(ProfileVersion, version_id)
    if not item:
        raise HTTPException(status_code=404, detail="Profile version not found")
    return get_version_detail(item)


@router.post("/profile-versions/{version_id}/sign", response_model=ProfileSignatureRead, status_code=status.HTTP_201_CREATED)
def sign_version(
    version_id: int,
    payload: SignProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "APPROVER")),
):
    return sign_profile_version(db, version_id, current_user, payload)


@router.get("/profiles/{profile_id}/signatures", response_model=Page[ProfileSignatureRead])
def list_profile_signatures(
    profile_id: int,
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
):
    total = db.scalar(select(func.count(ProfileSignature.id)).where(ProfileSignature.profile_id == profile_id)) or 0
    items = db.scalars(
        select(ProfileSignature).where(ProfileSignature.profile_id == profile_id).order_by(ProfileSignature.created_at.desc()).limit(limit).offset(offset)
    ).all()
    return Page[ProfileSignatureRead](items=items, total=total, limit=limit, offset=offset)


@router.get("/profile-signatures/{signature_id}", response_model=ProfileSignatureRead)
def get_signature(signature_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.get(ProfileSignature, signature_id)
    if not item:
        raise HTTPException(status_code=404, detail="Signature not found")
    return item


@router.get("/profile-signatures/{signature_id}/download")
def download_signature_file(signature_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.get(ProfileSignature, signature_id)
    if not item:
        raise HTTPException(status_code=404, detail="Signature not found")
    if not item.signed_file_path:
        raise HTTPException(status_code=404, detail="Signed file not generated")
    path = Path(item.signed_file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Physical signed file not found")
    return FileResponse(path=str(path), media_type="text/plain; charset=utf-8", filename=path.name)
