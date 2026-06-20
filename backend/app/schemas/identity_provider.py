from pydantic import BaseModel, EmailStr


class LdapConnectionTestRequest(BaseModel):
    server_uri: str | None = None
    bind_dn: str | None = None
    bind_password: str | None = None
    user_base_dn: str | None = None
    user_filter: str | None = None
    test_username: str | None = None


class LdapConnectionTestResult(BaseModel):
    mode: str
    enabled: bool
    dry_run: bool
    server_uri: str | None = None
    user_base_dn: str | None = None
    bind_configured: bool
    status: str
    message: str
    checklist: list[str]


class LdapUserPreviewRequest(BaseModel):
    username: str
    email: EmailStr | None = None
    full_name: str | None = None
    external_id: str | None = None
    role_code: str | None = "ATTT_OFFICER"
    organization_code: str | None = None


class LdapUserPreviewResult(BaseModel):
    username: str
    email: str | None = None
    full_name: str
    external_id: str
    auth_provider: str = "LDAP"
    role_code: str | None = None
    organization_code: str | None = None
    local_user_exists: bool
    action: str
    mapping_warnings: list[str]


class LdapUserSyncRequest(LdapUserPreviewRequest):
    is_active: bool = True
    allow_local_fallback: bool = False


class LdapUserSyncResult(BaseModel):
    id: int
    username: str
    email: str | None = None
    full_name: str
    auth_provider: str
    external_id: str | None = None
    role_id: int | None = None
    organization_id: int | None = None
    is_active: bool
    action: str


class SsoAssertionDryRunRequest(BaseModel):
    username: str
    email: EmailStr | None = None
    full_name: str | None = None
    external_id: str | None = None
    role_code: str | None = "ATTT_OFFICER"
    organization_code: str | None = None
    provider_name: str | None = None


class SsoAssertionDryRunResult(BaseModel):
    provider_name: str
    subject: str
    claims: dict
    mapped_user: LdapUserPreviewResult


class IdentityProductionReadiness(BaseModel):
    version: str
    ldap_enabled: bool
    ldap_dry_run: bool
    sso_enabled: bool
    sso_provider_name: str
    local_login_enabled: bool
    access_control_strict_org_scope: bool
    readiness_score: int
    status: str
    checks: list[dict]
    recommendations: list[str]
