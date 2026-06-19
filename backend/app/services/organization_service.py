from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.information_system import InformationSystem
from app.models.level_profile import LevelProfile
from app.models.organization import Organization
from app.models.user import User


def compute_org_level_path(db: Session, org: Organization) -> None:
    if org.parent_id:
        parent = db.get(Organization, org.parent_id)
        if parent:
            org.level = (parent.level or 1) + 1
            org.path = f"{parent.path or ('/' + parent.code)}/{org.code}"
            return
    org.level = 1
    org.path = f"/{org.code}"


def descendant_ids(db: Session, organization_id: int) -> list[int]:
    root = db.get(Organization, organization_id)
    if not root:
        return []
    root_path = root.path or f"/{root.code}"
    rows = db.scalars(select(Organization.id).where(Organization.path.like(f"{root_path}%"))).all()
    return list(rows)


def build_org_tree(db: Session) -> list[dict]:
    orgs = db.scalars(select(Organization).order_by(Organization.level.asc(), Organization.name.asc())).all()
    users_by_org = dict(db.execute(select(User.organization_id, func.count(User.id)).group_by(User.organization_id)).all())
    systems_by_org = dict(db.execute(select(InformationSystem.owner_org_id, func.count(InformationSystem.id)).group_by(InformationSystem.owner_org_id)).all())
    profiles_by_org: dict[int, int] = {}
    profile_rows = db.execute(
        select(InformationSystem.owner_org_id, func.count(LevelProfile.id))
        .join(LevelProfile, LevelProfile.information_system_id == InformationSystem.id)
        .group_by(InformationSystem.owner_org_id)
    ).all()
    profiles_by_org.update({k: v for k, v in profile_rows if k is not None})

    nodes = {}
    for org in orgs:
        data = {
            "id": org.id,
            "code": org.code,
            "name": org.name,
            "org_type": org.org_type,
            "description": org.description,
            "parent_id": org.parent_id,
            "level": org.level,
            "path": org.path,
            "is_active": org.is_active,
            "manager_name": org.manager_name,
            "contact_email": org.contact_email,
            "users_count": int(users_by_org.get(org.id, 0) or 0),
            "systems_count": int(systems_by_org.get(org.id, 0) or 0),
            "profiles_count": int(profiles_by_org.get(org.id, 0) or 0),
            "children": [],
        }
        nodes[org.id] = data

    roots = []
    for org in orgs:
        node = nodes[org.id]
        if org.parent_id and org.parent_id in nodes:
            nodes[org.parent_id]["children"].append(node)
        else:
            roots.append(node)
    return roots


def organization_scope_summary(db: Session, organization_id: int) -> dict | None:
    org = db.get(Organization, organization_id)
    if not org:
        return None
    ids = descendant_ids(db, organization_id) or [organization_id]
    users_count = db.scalar(select(func.count(User.id)).where(User.organization_id.in_(ids))) or 0
    systems_count = db.scalar(select(func.count(InformationSystem.id)).where(InformationSystem.owner_org_id.in_(ids))) or 0
    profiles_count = db.scalar(
        select(func.count(LevelProfile.id))
        .join(InformationSystem, InformationSystem.id == LevelProfile.information_system_id)
        .where(InformationSystem.owner_org_id.in_(ids))
    ) or 0

    def count_level(level: int) -> int:
        return db.scalar(select(func.count(InformationSystem.id)).where(InformationSystem.owner_org_id.in_(ids), InformationSystem.proposed_level == level)) or 0

    return {
        "organization": org,
        "descendant_organization_ids": ids,
        "users_count": users_count,
        "systems_count": systems_count,
        "profiles_count": profiles_count,
        "level_2_systems": count_level(2),
        "level_3_systems": count_level(3),
        "level_4_systems": count_level(4),
        "level_5_systems": count_level(5),
    }
