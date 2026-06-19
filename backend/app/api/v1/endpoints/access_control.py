from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.models.information_system import InformationSystem
from app.models.level_profile import LevelProfile
from app.models.user import User
from app.schemas.access_control import AccessCheckRead, AccessScopeRead, OrganizationAccessPolicy
from app.services.access_control_service import build_access_scope, can_access_information_system, can_access_profile

router = APIRouter()


@router.get("/access-control/my-scope", response_model=AccessScopeRead)
def my_access_scope(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return build_access_scope(db, current_user)


@router.get("/access-control/policy", response_model=OrganizationAccessPolicy)
def organization_access_policy(current_user: User = Depends(get_current_user)):
    return OrganizationAccessPolicy(
        strict_org_scope=settings.ACCESS_CONTROL_STRICT_ORG_SCOPE,
        description=(
            "Organization-based access foundation: non-admin users are scoped to records "
            "owned/operated by their organization or profiles they created."
        ),
    )


@router.get("/information-systems/{system_id}/access-check", response_model=AccessCheckRead)
def check_information_system_access(system_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    system = db.get(InformationSystem, system_id)
    allowed, reason = can_access_information_system(db, current_user, system)
    return AccessCheckRead(
        resource_type="information_system",
        resource_id=system_id,
        allowed=allowed,
        reason=reason,
        scope=AccessScopeRead(**build_access_scope(db, current_user)),
    )


@router.get("/profiles/{profile_id}/access-check", response_model=AccessCheckRead)
def check_profile_access(profile_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = db.get(LevelProfile, profile_id)
    allowed, reason = can_access_profile(db, current_user, profile)
    return AccessCheckRead(
        resource_type="level_profile",
        resource_id=profile_id,
        allowed=allowed,
        reason=reason,
        scope=AccessScopeRead(**build_access_scope(db, current_user)),
    )
