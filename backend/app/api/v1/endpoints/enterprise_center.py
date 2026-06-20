from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.enterprise_center import BackupRecord, DataRetentionPolicy, EnterpriseConfiguration, EnterpriseJobSchedule
from app.models.user import User
from app.schemas.common import Page
from app.schemas.enterprise_center import (
    BackupRecordCreate,
    BackupRecordRead,
    DataRetentionPolicyRead,
    DataRetentionPolicyUpsert,
    EnterpriseCenterDashboard,
    EnterpriseConfigurationRead,
    EnterpriseConfigurationUpsert,
    EnterpriseHealthDashboard,
    EnterpriseJobScheduleRead,
    EnterpriseJobScheduleUpsert,
    EnterpriseReadinessDashboard,
)
from app.services.enterprise_center_service import (
    create_backup_record,
    enterprise_dashboard,
    enterprise_readiness,
    run_health_checks,
    seed_enterprise_defaults,
    validate_backup_record,
)

router = APIRouter()


@router.get("/enterprise-center/dashboard", response_model=EnterpriseCenterDashboard)
def dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return enterprise_dashboard(db)


@router.post("/enterprise-center/seed-defaults")
def seed_defaults(db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    return seed_enterprise_defaults(db)


@router.get("/enterprise-center/readiness", response_model=EnterpriseReadinessDashboard)
def readiness(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return enterprise_readiness(db)


@router.get("/enterprise-center/health", response_model=EnterpriseHealthDashboard)
def health(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return run_health_checks(db)


@router.get("/enterprise-center/configurations", response_model=Page[EnterpriseConfigurationRead])
def list_configurations(
    config_group: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    seed_enterprise_defaults(db)
    stmt = select(EnterpriseConfiguration)
    count_stmt = select(func.count(EnterpriseConfiguration.id))
    if config_group:
        stmt = stmt.where(EnterpriseConfiguration.config_group == config_group.upper())
        count_stmt = count_stmt.where(EnterpriseConfiguration.config_group == config_group.upper())
    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(EnterpriseConfiguration.config_group, EnterpriseConfiguration.config_key).limit(limit).offset(offset)).all()
    return Page[EnterpriseConfigurationRead](items=items, total=total, limit=limit, offset=offset)


@router.post("/enterprise-center/configurations", response_model=EnterpriseConfigurationRead)
def upsert_configuration(
    payload: EnterpriseConfigurationUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    item = db.scalar(select(EnterpriseConfiguration).where(EnterpriseConfiguration.config_key == payload.config_key))
    if not item:
        item = EnterpriseConfiguration(config_key=payload.config_key)
        db.add(item)
    item.config_group = payload.config_group.upper()
    item.display_name = payload.display_name
    item.config_value = payload.config_value
    item.value_type = payload.value_type.upper()
    item.is_secret = payload.is_secret
    item.is_enabled = payload.is_enabled
    item.description = payload.description
    db.commit()
    db.refresh(item)
    return item


@router.get("/enterprise-center/jobs", response_model=Page[EnterpriseJobScheduleRead])
def list_jobs(
    job_group: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    seed_enterprise_defaults(db)
    stmt = select(EnterpriseJobSchedule)
    count_stmt = select(func.count(EnterpriseJobSchedule.id))
    if job_group:
        stmt = stmt.where(EnterpriseJobSchedule.job_group == job_group.upper())
        count_stmt = count_stmt.where(EnterpriseJobSchedule.job_group == job_group.upper())
    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(EnterpriseJobSchedule.job_group, EnterpriseJobSchedule.job_code).limit(limit).offset(offset)).all()
    return Page[EnterpriseJobScheduleRead](items=items, total=total, limit=limit, offset=offset)


@router.post("/enterprise-center/jobs", response_model=EnterpriseJobScheduleRead)
def upsert_job(
    payload: EnterpriseJobScheduleUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER")),
):
    item = db.scalar(select(EnterpriseJobSchedule).where(EnterpriseJobSchedule.job_code == payload.job_code))
    if not item:
        item = EnterpriseJobSchedule(job_code=payload.job_code)
        db.add(item)
    item.job_name = payload.job_name
    item.job_group = payload.job_group.upper()
    item.schedule_expression = payload.schedule_expression
    item.is_enabled = payload.is_enabled
    item.next_run_hint = payload.next_run_hint
    item.last_status = item.last_status or "READY"
    db.commit()
    db.refresh(item)
    return item


@router.post("/enterprise-center/jobs/{job_id}/toggle", response_model=EnterpriseJobScheduleRead)
def toggle_job(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    item = db.get(EnterpriseJobSchedule, job_id)
    if not item:
        raise HTTPException(status_code=404, detail="Job not found")
    item.is_enabled = not item.is_enabled
    db.commit()
    db.refresh(item)
    return item


@router.get("/enterprise-center/retention-policies", response_model=Page[DataRetentionPolicyRead])
def list_retention_policies(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    seed_enterprise_defaults(db)
    total = db.scalar(select(func.count(DataRetentionPolicy.id))) or 0
    items = db.scalars(select(DataRetentionPolicy).order_by(DataRetentionPolicy.data_domain).limit(limit).offset(offset)).all()
    return Page[DataRetentionPolicyRead](items=items, total=total, limit=limit, offset=offset)


@router.post("/enterprise-center/retention-policies", response_model=DataRetentionPolicyRead)
def upsert_retention_policy(
    payload: DataRetentionPolicyUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    item = db.scalar(select(DataRetentionPolicy).where(DataRetentionPolicy.policy_code == payload.policy_code))
    if not item:
        item = DataRetentionPolicy(policy_code=payload.policy_code)
        db.add(item)
    item.data_domain = payload.data_domain.upper()
    item.retention_days = payload.retention_days
    item.archive_enabled = payload.archive_enabled
    item.purge_enabled = payload.purge_enabled
    item.legal_hold = payload.legal_hold
    item.description = payload.description
    db.commit()
    db.refresh(item)
    return item


@router.get("/enterprise-center/backups", response_model=Page[BackupRecordRead])
def list_backups(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total = db.scalar(select(func.count(BackupRecord.id))) or 0
    items = db.scalars(select(BackupRecord).order_by(BackupRecord.started_at.desc(), BackupRecord.id.desc()).limit(limit).offset(offset)).all()
    return Page[BackupRecordRead](items=items, total=total, limit=limit, offset=offset)


@router.post("/enterprise-center/backups/mock", response_model=BackupRecordRead)
def create_mock_backup(
    payload: BackupRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER")),
):
    return create_backup_record(db, backup_type=payload.backup_type, scope=payload.scope, status=payload.status, storage_location=payload.storage_location, size_mb=payload.size_mb, notes=payload.notes)


@router.post("/enterprise-center/backups/{backup_id}/validate", response_model=BackupRecordRead)
def validate_backup(backup_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    try:
        return validate_backup_record(db, backup_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
