from pydantic import BaseModel


class AccessScopeRead(BaseModel):
    user_id: int
    username: str
    role_code: str | None = None
    organization_id: int | None = None
    scope_type: str
    can_manage_all_organizations: bool
    allowed_organization_ids: list[int]


class AccessCheckRead(BaseModel):
    resource_type: str
    resource_id: int
    allowed: bool
    reason: str
    scope: AccessScopeRead


class OrganizationAccessPolicy(BaseModel):
    strict_org_scope: bool
    admin_bypass: bool = True
    reviewer_cross_org_read: bool = True
    description: str
