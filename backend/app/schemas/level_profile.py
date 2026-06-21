from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class LevelProfileBase(BaseModel):
    profile_code: str = Field(min_length=3, max_length=100)
    information_system_id: int
    proposed_level: int = Field(ge=1, le=5)
    status: str = "DRAFT"
    basis_for_level: str | None = None
    system_scope_description: str | None = None
    technical_architecture: str | None = None
    confidentiality_impact: str | None = None
    integrity_impact: str | None = None
    availability_impact: str | None = None
    created_by: int | None = None
    locked_by: int | None = None
    is_deleted: bool = False
    deleted_at: datetime | None = None
    deleted_by: int | None = None


class LevelProfileCreate(LevelProfileBase):
    pass


class LevelProfileUpdate(BaseModel):
    profile_code: str | None = Field(default=None, min_length=3, max_length=100)
    information_system_id: int | None = None
    proposed_level: int | None = Field(default=None, ge=1, le=5)
    status: str | None = None
    basis_for_level: str | None = None
    system_scope_description: str | None = None
    technical_architecture: str | None = None
    confidentiality_impact: str | None = None
    integrity_impact: str | None = None
    availability_impact: str | None = None
    created_by: int | None = None
    locked_by: int | None = None
    is_deleted: bool = False
    deleted_at: datetime | None = None
    deleted_by: int | None = None


class LevelProfileRead(LevelProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
