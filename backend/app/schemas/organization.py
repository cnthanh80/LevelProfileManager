from pydantic import BaseModel, Field, ConfigDict


class OrganizationBase(BaseModel):
    code: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=3, max_length=255)
    org_type: str | None = None
    description: str | None = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=2, max_length=50)
    name: str | None = Field(default=None, min_length=3, max_length=255)
    org_type: str | None = None
    description: str | None = None


class OrganizationRead(OrganizationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
