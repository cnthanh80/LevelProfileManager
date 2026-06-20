from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
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
from app.services.identity_provider_service import (
    identity_readiness,
    ldap_test_connection,
    preview_ldap_user_mapping,
    sso_assertion_dry_run,
    sync_ldap_user,
)

router = APIRouter()


@router.get("/identity-provider/production-readiness", response_model=IdentityProductionReadiness)
def production_readiness(current_user: User = Depends(get_current_user)):
    return identity_readiness()


@router.post("/identity-provider/ldap/test-connection", response_model=LdapConnectionTestResult)
def test_ldap_connection(payload: LdapConnectionTestRequest, current_user: User = Depends(get_current_user)):
    return ldap_test_connection(payload)


@router.post("/identity-provider/ldap/preview-user", response_model=LdapUserPreviewResult)
def preview_ldap_user(payload: LdapUserPreviewRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return preview_ldap_user_mapping(db, payload)


@router.post("/identity-provider/ldap/sync-user", response_model=LdapUserSyncResult)
def sync_external_ldap_user(payload: LdapUserSyncRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return sync_ldap_user(db, payload)


@router.post("/identity-provider/sso/assertion-dry-run", response_model=SsoAssertionDryRunResult)
def dry_run_sso_assertion(payload: SsoAssertionDryRunRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return sso_assertion_dry_run(db, payload)
