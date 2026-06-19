from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def write_audit_log(
    db: Session,
    *,
    actor_id: int | None,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    detail: str | None = None,
    request_id: str | None = None,
    http_method: str | None = None,
    path: str | None = None,
    status_code: int | None = None,
    duration_ms: int | None = None,
    success: bool | None = None,
    source: str | None = "API",
) -> AuditLog:
    item = AuditLog(
        actor_id=actor_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        ip_address=ip_address,
        user_agent=user_agent,
        detail=detail,
        request_id=request_id,
        http_method=http_method,
        path=path,
        status_code=status_code,
        duration_ms=duration_ms,
        success=success,
        source=source,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
