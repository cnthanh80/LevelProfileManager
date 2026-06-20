from __future__ import annotations

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.organization import Organization
from app.models.role import Role
from app.models.user import User
from app.schemas.identity_provider import (
    IdentityProductionReadiness,
    LdapConnectionTestRequest,
    LdapConnectionTestResult,
    LdapUserPreviewRequest,
    LdapUserPreviewResult,
    LdapUserSyncRequest,
    LdapUserSyncResult,
    SsoAssertionDryRunRequest,
    SsoAssertionDryRunResult,
)
from sqlalchemy import select
from sqlalchemy.orm import Session


def _find_role(db: Session, role_code: str | None) -> Role | None:
    if not role_code:
        return None
    return db.scalar(select(Role).where(Role.code == role_code))


def _find_org(db: Session, org_code: str | None) -> Organization | None:
    if not org_code:
        return None
    return db.scalar(select(Organization).where(Organization.code == org_code))


def ldap_test_connection(payload: LdapConnectionTestRequest | None = None) -> LdapConnectionTestResult:
    payload = payload or LdapConnectionTestRequest()
    server_uri = payload.server_uri or settings.LDAP_SERVER_URI
    user_base_dn = payload.user_base_dn or settings.LDAP_USER_BASE_DN
    bind_dn = payload.bind_dn or settings.LDAP_BIND_DN
    dry_run = settings.LDAP_DRY_RUN
    enabled = settings.LDAP_ENABLED
    checklist: list[str] = []
    if server_uri:
        checklist.append("LDAP server URI configured")
    else:
        checklist.append("LDAP server URI missing")
    if user_base_dn:
        checklist.append("LDAP user base DN configured")
    else:
        checklist.append("LDAP user base DN missing")
    if bind_dn:
        checklist.append("LDAP bind DN configured")
    else:
        checklist.append("LDAP bind DN missing")
    if settings.LDAP_USER_FILTER:
        checklist.append("LDAP user filter configured")

    if dry_run:
        return LdapConnectionTestResult(
            mode="DRY_RUN",
            enabled=enabled,
            dry_run=True,
            server_uri=server_uri,
            user_base_dn=user_base_dn,
            bind_configured=bool(bind_dn),
            status="OK",
            message="LDAP production adapter is in dry-run mode. Configuration is validated without network bind.",
            checklist=checklist,
        )
    if not enabled:
        return LdapConnectionTestResult(
            mode="DISABLED",
            enabled=False,
            dry_run=False,
            server_uri=server_uri,
            user_base_dn=user_base_dn,
            bind_configured=bool(bind_dn),
            status="DISABLED",
            message="LDAP is disabled. Enable LDAP_ENABLED=true for production bind.",
            checklist=checklist,
        )
    if not server_uri or not user_base_dn or not bind_dn:
        return LdapConnectionTestResult(
            mode="PRODUCTION",
            enabled=True,
            dry_run=False,
            server_uri=server_uri,
            user_base_dn=user_base_dn,
            bind_configured=bool(bind_dn),
            status="CONFIG_INCOMPLETE",
            message="LDAP production mode requires server URI, bind DN and user base DN.",
            checklist=checklist,
        )
    return LdapConnectionTestResult(
        mode="PRODUCTION",
        enabled=True,
        dry_run=False,
        server_uri=server_uri,
        user_base_dn=user_base_dn,
        bind_configured=True,
        status="READY_FOR_BIND_ADAPTER",
        message="Configuration is complete. Wire ldap3 or enterprise SSO gateway in the deployment adapter.",
        checklist=checklist,
    )


def preview_ldap_user_mapping(db: Session, payload: LdapUserPreviewRequest) -> LdapUserPreviewResult:
    existing = db.scalar(select(User).where(User.username == payload.username))
    role = _find_role(db, payload.role_code)
    org = _find_org(db, payload.organization_code)
    warnings: list[str] = []
    if payload.role_code and not role:
        warnings.append(f"Role code not found: {payload.role_code}")
    if payload.organization_code and not org:
        warnings.append(f"Organization code not found: {payload.organization_code}")
    full_name = payload.full_name or payload.username
    external_id = payload.external_id or f"LDAP:{payload.username}"
    return LdapUserPreviewResult(
        username=payload.username,
        email=str(payload.email) if payload.email else None,
        full_name=full_name,
        external_id=external_id,
        role_code=role.code if role else payload.role_code,
        organization_code=org.code if org else payload.organization_code,
        local_user_exists=existing is not None,
        action="UPDATE_EXISTING_USER" if existing else "CREATE_EXTERNAL_USER",
        mapping_warnings=warnings,
    )


def sync_ldap_user(db: Session, payload: LdapUserSyncRequest) -> LdapUserSyncResult:
    existing = db.scalar(select(User).where(User.username == payload.username))
    role = _find_role(db, payload.role_code)
    org = _find_org(db, payload.organization_code)
    full_name = payload.full_name or payload.username
    external_id = payload.external_id or f"LDAP:{payload.username}"
    action = "UPDATED"
    if existing:
        user = existing
    else:
        user = User(
            username=payload.username,
            hashed_password=get_password_hash(f"LDAP_DISABLED_{payload.username}_ChangeMe@123"),
            full_name=full_name,
            is_active=payload.is_active,
        )
        db.add(user)
        action = "CREATED"
    user.email = str(payload.email) if payload.email else user.email
    user.full_name = full_name
    user.auth_provider = "LDAP"
    user.external_id = external_id
    user.is_local_auth_allowed = payload.allow_local_fallback
    user.is_active = payload.is_active
    if role:
        user.role_id = role.id
    if org:
        user.organization_id = org.id
    db.commit()
    db.refresh(user)
    return LdapUserSyncResult(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        auth_provider=user.auth_provider,
        external_id=user.external_id,
        role_id=user.role_id,
        organization_id=user.organization_id,
        is_active=user.is_active,
        action=action,
    )


def sso_assertion_dry_run(db: Session, payload: SsoAssertionDryRunRequest) -> SsoAssertionDryRunResult:
    provider_name = payload.provider_name or settings.SSO_PROVIDER_NAME
    preview = preview_ldap_user_mapping(
        db,
        LdapUserPreviewRequest(
            username=payload.username,
            email=payload.email,
            full_name=payload.full_name,
            external_id=payload.external_id or f"SSO:{provider_name}:{payload.username}",
            role_code=payload.role_code,
            organization_code=payload.organization_code,
        ),
    )
    claims = {
        "sub": payload.external_id or f"SSO:{provider_name}:{payload.username}",
        "preferred_username": payload.username,
        "email": str(payload.email) if payload.email else None,
        "name": payload.full_name or payload.username,
        "role_code": payload.role_code,
        "organization_code": payload.organization_code,
        "provider": provider_name,
    }
    return SsoAssertionDryRunResult(provider_name=provider_name, subject=claims["sub"], claims=claims, mapped_user=preview)


def identity_readiness() -> IdentityProductionReadiness:
    checks = [
        {"name": "LDAP enabled", "passed": bool(settings.LDAP_ENABLED), "detail": "LDAP_ENABLED controls enterprise directory login."},
        {"name": "LDAP dry-run disabled for production", "passed": not bool(settings.LDAP_DRY_RUN), "detail": "Set LDAP_DRY_RUN=false before real production bind."},
        {"name": "LDAP server URI", "passed": bool(settings.LDAP_SERVER_URI), "detail": settings.LDAP_SERVER_URI or "Not configured"},
        {"name": "LDAP user base DN", "passed": bool(settings.LDAP_USER_BASE_DN), "detail": settings.LDAP_USER_BASE_DN or "Not configured"},
        {"name": "SSO configured", "passed": bool(settings.SSO_ENABLED and settings.SSO_LOGIN_URL), "detail": settings.SSO_PROVIDER_NAME},
        {"name": "Strict organization scope", "passed": bool(settings.ACCESS_CONTROL_STRICT_ORG_SCOPE), "detail": "Recommended for banking/government deployment."},
    ]
    passed = sum(1 for item in checks if item["passed"])
    score = round((passed / len(checks)) * 100)
    status = "PRODUCTION_READY" if score >= 80 else "FOUNDATION_READY" if score >= 50 else "CONFIG_REQUIRED"
    recommendations: list[str] = []
    if settings.LDAP_DRY_RUN:
        recommendations.append("Disable LDAP_DRY_RUN and test bind/search through the enterprise LDAP adapter.")
    if not settings.SSO_ENABLED:
        recommendations.append("Configure SSO metadata/login URL when moving to centralized identity provider.")
    if not settings.ACCESS_CONTROL_STRICT_ORG_SCOPE:
        recommendations.append("Enable strict organization scope for production data isolation.")
    return IdentityProductionReadiness(
        version=settings.APP_VERSION,
        ldap_enabled=settings.LDAP_ENABLED,
        ldap_dry_run=settings.LDAP_DRY_RUN,
        sso_enabled=settings.SSO_ENABLED,
        sso_provider_name=settings.SSO_PROVIDER_NAME,
        local_login_enabled=True,
        access_control_strict_org_scope=settings.ACCESS_CONTROL_STRICT_ORG_SCOPE,
        readiness_score=score,
        status=status,
        checks=checks,
        recommendations=recommendations,
    )
