from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditActionItem, AuditLogCreate, AuditLogRead, AuditLogSummary
from app.schemas.common import Page
from app.services.audit_service import write_audit_log

router = APIRouter()


def _apply_filters(stmt, *, action=None, entity_type=None, actor_id=None, success=None, http_method=None, path_contains=None, status_code=None):
    filters = []
    if action:
        filters.append(AuditLog.action == action)
    if entity_type:
        filters.append(AuditLog.entity_type == entity_type)
    if actor_id is not None:
        filters.append(AuditLog.actor_id == actor_id)
    if success is not None:
        filters.append(AuditLog.success == success)
    if http_method:
        filters.append(AuditLog.http_method == http_method.upper())
    if path_contains:
        filters.append(AuditLog.path.ilike(f"%{path_contains}%"))
    if status_code is not None:
        filters.append(AuditLog.status_code == status_code)
    if filters:
        stmt = stmt.where(*filters)
    return stmt


@router.get("/audit-logs", response_model=Page[AuditLogRead])
def list_audit_logs(
    db: Session = Depends(get_db),
    action: str | None = Query(default=None),
    entity_type: str | None = Query(default=None),
    actor_id: int | None = Query(default=None),
    success: bool | None = Query(default=None),
    http_method: str | None = Query(default=None),
    path_contains: str | None = Query(default=None),
    status_code: int | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REPORT_VIEWER")),
):
    stmt = _apply_filters(select(AuditLog), action=action, entity_type=entity_type, actor_id=actor_id, success=success, http_method=http_method, path_contains=path_contains, status_code=status_code)
    count_stmt = _apply_filters(select(func.count(AuditLog.id)), action=action, entity_type=entity_type, actor_id=actor_id, success=success, http_method=http_method, path_contains=path_contains, status_code=status_code)
    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(AuditLog.created_at.desc(), AuditLog.id.desc()).limit(limit).offset(offset)).all()
    return Page[AuditLogRead](items=items, total=total, limit=limit, offset=offset)


@router.get("/audit-logs/summary", response_model=AuditLogSummary)
def audit_log_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REPORT_VIEWER")),
):
    total = db.scalar(select(func.count(AuditLog.id))) or 0
    success_count = db.scalar(select(func.count(AuditLog.id)).where(AuditLog.success.is_(True))) or 0
    failed_count = db.scalar(select(func.count(AuditLog.id)).where(AuditLog.success.is_(False))) or 0
    by_action_rows = db.execute(select(AuditLog.action, func.count(AuditLog.id)).group_by(AuditLog.action)).all()
    by_entity_rows = db.execute(select(AuditLog.entity_type, func.count(AuditLog.id)).group_by(AuditLog.entity_type)).all()
    by_method_rows = db.execute(select(AuditLog.http_method, func.count(AuditLog.id)).where(AuditLog.http_method.is_not(None)).group_by(AuditLog.http_method)).all()
    by_status_rows = db.execute(select(AuditLog.status_code, func.count(AuditLog.id)).where(AuditLog.status_code.is_not(None)).group_by(AuditLog.status_code)).all()
    return AuditLogSummary(
        total=total,
        success=success_count,
        failed=failed_count,
        by_action={row[0]: row[1] for row in by_action_rows if row[0]},
        by_entity_type={row[0]: row[1] for row in by_entity_rows if row[0]},
        by_http_method={row[0]: row[1] for row in by_method_rows if row[0]},
        by_status_code={str(row[0]): row[1] for row in by_status_rows if row[0] is not None},
    )


@router.get("/audit-logs/actions", response_model=list[AuditActionItem])
def audit_actions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REPORT_VIEWER")),
):
    rows = db.execute(select(AuditLog.action, func.count(AuditLog.id)).group_by(AuditLog.action).order_by(func.count(AuditLog.id).desc())).all()
    return [AuditActionItem(action=row[0], count=row[1]) for row in rows]


@router.get("/profiles/{profile_id}/audit-trail", response_model=list[AuditLogRead])
def profile_audit_trail(
    profile_id: int,
    db: Session = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=300),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REVIEWER", "APPROVER", "REPORT_VIEWER")),
):
    # Combines direct entity audit records and request traces containing the profile path.
    stmt = (
        select(AuditLog)
        .where(
            (AuditLog.entity_id == profile_id)
            | (AuditLog.path.ilike(f"%/profiles/{profile_id}/%"))
            | (AuditLog.path.ilike(f"%/level-profiles/{profile_id}%"))
        )
        .order_by(AuditLog.created_at.desc(), AuditLog.id.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


@router.post("/audit-logs/manual", response_model=AuditLogRead, status_code=status.HTTP_201_CREATED)
def create_manual_audit_log(
    payload: AuditLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER")),
):
    return write_audit_log(
        db,
        actor_id=current_user.id,
        action=payload.action.upper(),
        entity_type=payload.entity_type.upper(),
        entity_id=payload.entity_id,
        detail=payload.detail,
        source=payload.source.upper(),
        success=True,
    )


@router.get("/audit-logs/export.csv")
def export_audit_logs_csv(
    db: Session = Depends(get_db),
    limit: int = Query(default=500, ge=1, le=5000),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REPORT_VIEWER")),
):
    rows = db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc(), AuditLog.id.desc()).limit(limit)).all()
    header = "id,created_at,actor_id,action,entity_type,entity_id,method,path,status_code,duration_ms,success,source\n"
    lines = [header]
    for item in rows:
        values = [
            item.id,
            item.created_at.isoformat() if item.created_at else "",
            item.actor_id or "",
            item.action,
            item.entity_type,
            item.entity_id or "",
            item.http_method or "",
            (item.path or "").replace(',', ' '),
            item.status_code or "",
            item.duration_ms or "",
            item.success if item.success is not None else "",
            item.source or "",
        ]
        lines.append(",".join(str(v) for v in values) + "\n")
    return Response(content="".join(lines), media_type="text/csv")
