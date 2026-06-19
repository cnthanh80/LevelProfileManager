from fastapi import APIRouter, Depends

from app.api.deps import require_roles
from app.core.config import get_cors_origins, settings
from app.schemas.system import ProductionChecklistResponse, RuntimeSettingsResponse

router = APIRouter(prefix="/system")


@router.get("/runtime", response_model=RuntimeSettingsResponse)
def runtime_settings(_=Depends(require_roles("ADMIN"))):
    return RuntimeSettingsResponse(
        app_name=settings.APP_NAME,
        app_version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        debug=settings.DEBUG,
        api_prefix=settings.API_V1_PREFIX,
        cors_allowed_origins=get_cors_origins(),
        security_headers_enabled=settings.SECURITY_HEADERS_ENABLED,
        rate_limit_enabled=settings.RATE_LIMIT_ENABLED,
        rate_limit_requests_per_minute=settings.RATE_LIMIT_REQUESTS_PER_MINUTE,
        notification_dry_run=settings.NOTIFICATION_DRY_RUN,
        ldap_enabled=settings.LDAP_ENABLED,
        sso_enabled=settings.SSO_ENABLED,
    )


@router.get("/production-checklist", response_model=ProductionChecklistResponse)
def production_checklist(_=Depends(require_roles("ADMIN"))):
    origins = get_cors_origins()
    notes: list[str] = []
    if "*" in origins:
        notes.append("CORS is open. Restrict CORS_ALLOWED_ORIGINS before production.")
    if settings.NOTIFICATION_DRY_RUN:
        notes.append("Notification engine is in dry-run mode.")
    if not settings.RATE_LIMIT_ENABLED:
        notes.append("Rate limit is disabled by default for local development.")
    if not (settings.LDAP_ENABLED or settings.SSO_ENABLED):
        notes.append("LDAP/SSO is not enabled. Local auth is being used.")

    return ProductionChecklistResponse(
        database_pool_pre_ping=True,
        security_headers_enabled=settings.SECURITY_HEADERS_ENABLED,
        rate_limit_configured=settings.RATE_LIMIT_ENABLED,
        audit_middleware_enabled=True,
        notification_dry_run=settings.NOTIFICATION_DRY_RUN,
        ldap_or_sso_ready=settings.LDAP_ENABLED or settings.SSO_ENABLED,
        cors_restricted="*" not in origins,
        notes=notes,
    )
