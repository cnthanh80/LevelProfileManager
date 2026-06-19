from pydantic import BaseModel, ConfigDict, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    description: str | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr | None = None
    full_name: str
    role_id: int | None = None
    organization_id: int | None = None
    is_active: bool


class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    email: EmailStr | None = None
    role_id: int | None = None
    organization_id: int | None = None
    is_active: bool = True


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
