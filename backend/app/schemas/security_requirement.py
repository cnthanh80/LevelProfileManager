from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class SecurityRequirementBase(BaseModel):
    code: str = Field(min_length=2, max_length=50)
    title: str = Field(min_length=3, max_length=500)
    description: str | None = None
    group_name: str = Field(min_length=2, max_length=100, description="MANAGEMENT hoặc TECHNICAL")
    category: str = Field(min_length=2, max_length=100)
    required_level: int = Field(ge=1, le=5)
    is_mandatory: bool = True
    sort_order: int = 0


class SecurityRequirementCreate(SecurityRequirementBase):
    pass


class SecurityRequirementUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=2, max_length=50)
    title: str | None = Field(default=None, min_length=3, max_length=500)
    description: str | None = None
    group_name: str | None = Field(default=None, min_length=2, max_length=100)
    category: str | None = Field(default=None, min_length=2, max_length=100)
    required_level: int | None = Field(default=None, ge=1, le=5)
    is_mandatory: bool | None = None
    sort_order: int | None = None


class SecurityRequirementRead(SecurityRequirementBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
