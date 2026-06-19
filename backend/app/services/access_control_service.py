from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.information_system import InformationSystem
from app.models.level_profile import LevelProfile
from app.models.organization import Organization
from app.models.role import Role
from app.models.user import User

ADMIN_ROLES = {"ADMIN"}
CROSS_ORG_READ_ROLES = {"ADMIN", "REVIEWER", "APPROVER"}


def get_role_code(db: Session, user: User) -> str | None:
    if not user.role_id:
        return None
    role = db.get(Role, user.role_id)
    return role.code if role else None


def build_access_scope(db: Session, user: User) -> dict:
    role_code = get_role_code(db, user)
    can_manage_all = role_code in ADMIN_ROLES
    allowed_orgs: list[int] = []
    if user.organization_id:
        org = db.get(Organization, user.organization_id)
        if org and org.path:
            allowed_orgs = list(db.scalars(select(Organization.id).where(Organization.path.like(f"{org.path}%"))).all())
        else:
            allowed_orgs.append(user.organization_id)
    return {
        "user_id": user.id,
        "username": user.username,
        "role_code": role_code,
        "organization_id": user.organization_id,
        "scope_type": "GLOBAL" if can_manage_all else "ORGANIZATION",
        "can_manage_all_organizations": can_manage_all,
        "allowed_organization_ids": allowed_orgs,
    }


def can_access_information_system(db: Session, user: User, system: InformationSystem | None) -> tuple[bool, str]:
    if system is None:
        return False, "Information system not found"
    role_code = get_role_code(db, user)
    if role_code in ADMIN_ROLES:
        return True, "ADMIN role has global access"
    if role_code in CROSS_ORG_READ_ROLES and not settings.ACCESS_CONTROL_STRICT_ORG_SCOPE:
        return True, f"{role_code} role has cross-organization read access"
    if not user.organization_id:
        return False, "User is not assigned to an organization"
    scope = build_access_scope(db, user)
    allowed_orgs = set(scope.get("allowed_organization_ids", []))
    if system.owner_org_id in allowed_orgs or system.operator_org_id in allowed_orgs:
        return True, "User organization scope matches owner/operator organization"
    if system.manager_user_id == user.id:
        return True, "User is the assigned system manager"
    return False, "User organization is outside the resource scope"


def can_access_profile(db: Session, user: User, profile: LevelProfile | None) -> tuple[bool, str]:
    if profile is None:
        return False, "Profile not found"
    role_code = get_role_code(db, user)
    if role_code in ADMIN_ROLES:
        return True, "ADMIN role has global access"
    if profile.created_by == user.id:
        return True, "User created this profile"
    system = db.get(InformationSystem, profile.information_system_id)
    return can_access_information_system(db, user, system)
