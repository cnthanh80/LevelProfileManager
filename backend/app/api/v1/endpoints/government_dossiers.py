from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.government_dossier import GovernmentDossier, GovernmentDossierFile
from app.models.user import User
from app.schemas.common import Page
from app.schemas.government_dossier import (
    GovernmentDossierDetail,
    GovernmentDossierFileRead,
    GovernmentDossierGenerateRequest,
    GovernmentDossierRead,
    GovernmentDossierSummary,
)
from app.services.government_dossier_service import generate_government_dossier, list_dossier_files, delete_physical_dossier

router = APIRouter()


@router.get('/dossiers/summary', response_model=GovernmentDossierSummary)
def dossier_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dossiers = db.scalars(select(GovernmentDossier)).all()
    files_count = db.scalar(select(func.count(GovernmentDossierFile.id))) or 0
    latest: dict[str, int] = {}
    for d in dossiers:
        latest[str(d.profile_id)] = max(latest.get(str(d.profile_id), 0), d.version)
    return GovernmentDossierSummary(
        total_dossiers=len(dossiers),
        latest_version_by_profile=latest,
        generated_files=files_count,
        total_package_size=sum(d.package_size or 0 for d in dossiers),
    )


@router.post('/dossiers/{profile_id}/generate', response_model=GovernmentDossierDetail, status_code=status.HTTP_201_CREATED)
def generate_dossier(
    profile_id: int,
    payload: GovernmentDossierGenerateRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles('ADMIN', 'SECURITY_OFFICER', 'REVIEWER', 'APPROVER')),
):
    try:
        payload = payload or GovernmentDossierGenerateRequest()
        dossier = generate_government_dossier(
            db,
            profile_id=profile_id,
            generated_by=current_user.id,
            include_evidence=payload.include_evidence,
            notes=payload.notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return GovernmentDossierDetail.model_validate(dossier).model_copy(update={'files': [GovernmentDossierFileRead.model_validate(f) for f in list_dossier_files(db, dossier.id)]})


@router.get('/dossiers', response_model=Page[GovernmentDossierRead])
def list_dossiers(
    db: Session = Depends(get_db),
    profile_id: int | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias='status'),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
):
    stmt = select(GovernmentDossier)
    count_stmt = select(func.count(GovernmentDossier.id))
    filters = []
    if profile_id is not None:
        filters.append(GovernmentDossier.profile_id == profile_id)
    if status_filter:
        filters.append(GovernmentDossier.status == status_filter.upper())
    if filters:
        stmt = stmt.where(*filters)
        count_stmt = count_stmt.where(*filters)
    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(GovernmentDossier.created_at.desc(), GovernmentDossier.id.desc()).limit(limit).offset(offset)).all()
    return Page[GovernmentDossierRead](items=items, total=total, limit=limit, offset=offset)


@router.get('/dossiers/{dossier_id}', response_model=GovernmentDossierDetail)
def get_dossier(dossier_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dossier = db.get(GovernmentDossier, dossier_id)
    if not dossier:
        raise HTTPException(status_code=404, detail='Government dossier not found')
    return GovernmentDossierDetail.model_validate(dossier).model_copy(update={'files': [GovernmentDossierFileRead.model_validate(f) for f in list_dossier_files(db, dossier.id)]})


@router.get('/dossiers/{dossier_id}/files', response_model=list[GovernmentDossierFileRead])
def get_dossier_files(dossier_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not db.get(GovernmentDossier, dossier_id):
        raise HTTPException(status_code=404, detail='Government dossier not found')
    return list_dossier_files(db, dossier_id)


@router.get('/dossiers/{dossier_id}/download')
def download_dossier(dossier_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dossier = db.get(GovernmentDossier, dossier_id)
    if not dossier:
        raise HTTPException(status_code=404, detail='Government dossier not found')
    path = Path(dossier.package_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail='Physical package not found')
    return FileResponse(path=str(path), media_type='application/zip', filename=dossier.package_filename)


@router.get('/dossier-files/{file_id}/download')
def download_dossier_file(file_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.get(GovernmentDossierFile, file_id)
    if not item:
        raise HTTPException(status_code=404, detail='Government dossier file not found')
    path = Path(item.file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail='Physical file not found')
    return FileResponse(path=str(path), media_type=item.content_type or 'application/octet-stream', filename=item.file_name)


@router.post('/dossiers/{dossier_id}/regenerate', response_model=GovernmentDossierDetail, status_code=status.HTTP_201_CREATED)
def regenerate_dossier(
    dossier_id: int,
    payload: GovernmentDossierGenerateRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles('ADMIN', 'SECURITY_OFFICER', 'REVIEWER', 'APPROVER')),
):
    old = db.get(GovernmentDossier, dossier_id)
    if not old:
        raise HTTPException(status_code=404, detail='Government dossier not found')
    payload = payload or GovernmentDossierGenerateRequest()
    dossier = generate_government_dossier(
        db,
        profile_id=old.profile_id,
        generated_by=current_user.id,
        include_evidence=payload.include_evidence,
        notes=payload.notes or f'Regenerated from dossier {old.id}',
    )
    return GovernmentDossierDetail.model_validate(dossier).model_copy(update={'files': [GovernmentDossierFileRead.model_validate(f) for f in list_dossier_files(db, dossier.id)]})


@router.delete('/dossiers/{dossier_id}')
def delete_dossier(
    dossier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles('ADMIN', 'SECURITY_OFFICER')),
):
    dossier = db.get(GovernmentDossier, dossier_id)
    if not dossier:
        raise HTTPException(status_code=404, detail='Government dossier not found')
    files = list_dossier_files(db, dossier.id)
    for f in files:
        db.delete(f)
    db.delete(dossier)
    db.commit()
    delete_physical_dossier(dossier)
    return {'status': 'deleted', 'dossier_id': dossier_id}
