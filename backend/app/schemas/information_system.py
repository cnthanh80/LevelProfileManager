from pydantic import BaseModel, Field, ConfigDict, field_validator


class InformationSystemBase(BaseModel):
    code: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=3, max_length=255)
    owner_org_id: int | None = None
    operator_org_id: int | None = None
    manager_user_id: int | None = None
    purpose: str | None = None
    scope: str | None = None
    main_functions: str | None = None
    user_groups: str | None = None
    data_types: str | None = None
    importance_level: str | None = None
    deployment_model: str | None = Field(default=None, description="on_premise/cloud/hybrid")
    environment: str | None = Field(default=None, description="production/dr/test")
    operation_status: str = "active"
    proposed_level: int | None = Field(default=None, ge=1, le=5)


class InformationSystemCreate(InformationSystemBase):
    pass


class InformationSystemUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=2, max_length=50)
    name: str | None = Field(default=None, min_length=3, max_length=255)
    owner_org_id: int | None = None
    operator_org_id: int | None = None
    manager_user_id: int | None = None
    purpose: str | None = None
    scope: str | None = None
    main_functions: str | None = None
    user_groups: str | None = None
    data_types: str | None = None
    importance_level: str | None = None
    deployment_model: str | None = None
    environment: str | None = None
    operation_status: str | None = None
    proposed_level: int | None = Field(default=None, ge=1, le=5)


class InformationSystemRead(InformationSystemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
