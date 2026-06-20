from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.models.signature_provider import SignatureProvider
from app.models.signature_request import SignatureRequest
from app.models.user import User
from app.schemas.common import Page
from app.schemas.real_signature import (
    RealSignRequestCreate,
    SignatureCallbackPayload,
    SignatureGatewayStatus,
    SignatureProviderCreate,
    SignatureProviderRead,
    SignatureProviderUpdate,
    SignatureRequestRead,
)
from app.services.real_signature_service import create_sign_request, seed_default_signature_providers, signature_gateway_status, simulate_sign_request, complete_sign_request

router = APIRouter()


@router.get("/signature-gateway/status", response_model=SignatureGatewayStatus)
def gateway_status(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return signature_gateway_status(db)


@router.post("/signature-providers/seed-defaults")
def seed_providers(db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN"))):
    seed_default_signature_providers(db)
    return {"status": "ok", "message": "Default signature providers seeded"}


@router.get("/signature-providers", response_model=Page[SignatureProviderRead])
def list_providers(
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
):
    total = db.scalar(select(func.count(SignatureProvider.id))) or 0
    items = db.scalars(select(SignatureProvider).order_by(SignatureProvider.code).limit(limit).offset(offset)).all()
    return Page[SignatureProviderRead](items=items, total=total, limit=limit, offset=offset)


@router.post("/signature-providers", response_model=SignatureProviderRead, status_code=status.HTTP_201_CREATED)
def create_provider(payload: SignatureProviderCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN"))):
    exists = db.scalar(select(SignatureProvider).where(SignatureProvider.code == payload.code))
    if exists:
        raise HTTPException(status_code=409, detail="Provider code already exists")
    item = SignatureProvider(**payload.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return item


@router.put("/signature-providers/{provider_id}", response_model=SignatureProviderRead)
def update_provider(provider_id: int, payload: SignatureProviderUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN"))):
    item = db.get(SignatureProvider, provider_id)
    if not item:
        raise HTTPException(status_code=404, detail="Provider not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.commit(); db.refresh(item)
    return item


@router.post("/profile-versions/{version_id}/real-sign-requests", response_model=SignatureRequestRead, status_code=status.HTTP_201_CREATED)
def create_real_sign_request(
    version_id: int,
    payload: RealSignRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "APPROVER")),
):
    try:
        return create_sign_request(db, version_id, payload, current_user)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/signature-requests", response_model=Page[SignatureRequestRead])
def list_signature_requests(
    db: Session = Depends(get_db),
    status_filter: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
):
    stmt = select(SignatureRequest)
    count_stmt = select(func.count(SignatureRequest.id))
    if status_filter:
        stmt = stmt.where(SignatureRequest.status == status_filter)
        count_stmt = count_stmt.where(SignatureRequest.status == status_filter)
    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(SignatureRequest.created_at.desc()).limit(limit).offset(offset)).all()
    return Page[SignatureRequestRead](items=items, total=total, limit=limit, offset=offset)


@router.post("/signature-requests/{request_code}/simulate-callback", response_model=SignatureRequestRead)
def simulate_callback(request_code: str, db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "APPROVER"))):
    try:
        return simulate_sign_request(db, request_code)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/signature-requests/{request_code}/callback", response_model=SignatureRequestRead)
def provider_callback(request_code: str, payload: SignatureCallbackPayload, db: Session = Depends(get_db)):
    try:
        return complete_sign_request(db, request_code, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
