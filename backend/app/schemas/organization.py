from pydantic import BaseModel, Field, ConfigDict, EmailStr


class OrganizationBase(BaseModel):
    code: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=3, max_length=255)
    org_type: str | None = None
    description: str | None = None
    parent_id: int | None = None
    is_active: bool = True
    manager_name: str | None = None
    contact_email: EmailStr | None = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=2, max_length=50)
    name: str | None = Field(default=None, min_length=3, max_length=255)
    org_type: str | None = None
    description: str | None = None
    parent_id: int | None = None
    is_active: bool | None = None
    manager_name: str | None = None
    contact_email: EmailStr | None = None


class OrganizationRead(OrganizationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    level: int = 1
    path: str | None = None


class OrganizationTreeNode(OrganizationRead):
    children: list["OrganizationTreeNode"] = []
    users_count: int = 0
    systems_count: int = 0
    profiles_count: int = 0


class OrganizationScopeSummary(BaseModel):
    organization: OrganizationRead
    descendant_organization_ids: list[int]
    users_count: int
    systems_count: int
    profiles_count: int
    level_2_systems: int
    level_3_systems: int
    level_4_systems: int
    level_5_systems: int


OrganizationTreeNode.model_rebuild()
