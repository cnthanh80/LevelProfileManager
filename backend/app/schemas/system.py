from pydantic import BaseModel


class RuntimeSettingsResponse(BaseModel):
    app_name: str
    app_version: str
    environment: str
    debug: bool
    api_prefix: str
    cors_allowed_origins: list[str]
    security_headers_enabled: bool
    rate_limit_enabled: bool
    rate_limit_requests_per_minute: int
    notification_dry_run: bool
    ldap_enabled: bool
    sso_enabled: bool


class ProductionChecklistResponse(BaseModel):
    database_pool_pre_ping: bool
    security_headers_enabled: bool
    rate_limit_configured: bool
    audit_middleware_enabled: bool
    notification_dry_run: bool
    ldap_or_sso_ready: bool
    cors_restricted: bool
    notes: list[str]
