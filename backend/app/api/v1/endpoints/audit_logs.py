from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditLogRead
from app.schemas.common import Page

router = APIRouter()


@router.get("/audit-logs", response_model=Page[AuditLogRead])
def list_audit_logs(
    db: Session = Depends(get_db),
    action: str | None = Query(default=None),
    entity_type: str | None = Query(default=None),
    actor_id: int | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REPORT_VIEWER")),
):
    stmt = select(AuditLog)
    count_stmt = select(func.count(AuditLog.id))
    filters = []
    if action:
        filters.append(AuditLog.action == action)
    if entity_type:
        filters.append(AuditLog.entity_type == entity_type)
    if actor_id is not None:
        filters.append(AuditLog.actor_id == actor_id)
    if filters:
        stmt = stmt.where(*filters)
        count_stmt = count_stmt.where(*filters)
    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(AuditLog.created_at.desc(), AuditLog.id.desc()).limit(limit).offset(offset)).all()
    return Page[AuditLogRead](items=items, total=total, limit=limit, offset=offset)
