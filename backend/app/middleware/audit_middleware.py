import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.models.user import User
from app.services.audit_service import write_audit_log
from sqlalchemy import select


SKIP_PREFIXES = (
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/health",
    "/favicon.ico",
)


class AuditMiddleware(BaseHTTPMiddleware):
    """Lightweight HTTP audit trail.

    The middleware records API request metadata only. It intentionally does not
    capture request/response bodies to avoid storing sensitive data in audit logs.
    """

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path.startswith(SKIP_PREFIXES):
            return await call_next(request)

        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:32]
        started = time.perf_counter()
        response = None
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration_ms = int((time.perf_counter() - started) * 1000)
            actor_id = None
            authorization = request.headers.get("Authorization", "")
            if authorization.lower().startswith("bearer "):
                token = authorization.split(" ", 1)[1].strip()
                try:
                    payload = decode_access_token(token)
                    username = payload.get("sub")
                    if username:
                        with SessionLocal() as db:
                            user = db.scalar(select(User).where(User.username == username))
                            if user:
                                actor_id = user.id
                except Exception:
                    actor_id = None

            action = f"HTTP_{request.method.upper()}"
            entity_type = "API_REQUEST"
            detail = f"{request.method.upper()} {path}"
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
            try:
                with SessionLocal() as db:
                    write_audit_log(
                        db,
                        actor_id=actor_id,
                        action=action,
                        entity_type=entity_type,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        detail=detail,
                        request_id=request_id,
                        http_method=request.method.upper(),
                        path=path,
                        status_code=status_code,
                        duration_ms=duration_ms,
                        success=200 <= status_code < 400,
                        source="HTTP_MIDDLEWARE",
                    )
            except Exception:
                # Audit logging must never break business requests.
                pass

            if response is not None:
                response.headers["X-Request-ID"] = request_id
