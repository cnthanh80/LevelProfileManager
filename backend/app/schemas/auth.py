from datetime import datetime
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
    auth_provider: str = "LOCAL"
    external_id: str | None = None
    is_local_auth_allowed: bool = True
    failed_login_count: int = 0
    locked_until: datetime | None = None
    last_login_at: datetime | None = None
    must_change_password: bool = False


class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    email: EmailStr | None = None
    role_id: int | None = None
    organization_id: int | None = None
    is_active: bool = True
    auth_provider: str = "LOCAL"
    external_id: str | None = None
    is_local_auth_allowed: bool = True
    failed_login_count: int = 0
    locked_until: datetime | None = None
    last_login_at: datetime | None = None
    must_change_password: bool = False


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class LdapLoginRequest(BaseModel):
    username: str
    password: str


class IdentityProviderStatus(BaseModel):
    local_login_enabled: bool
    ldap_enabled: bool
    ldap_dry_run: bool
    sso_enabled: bool
    sso_provider_name: str
    sso_login_url: str | None = None


class SsoLoginHint(BaseModel):
    enabled: bool
    provider_name: str
    login_url: str | None = None
    message: str


class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None
    full_name: str | None = None
    email: EmailStr | None = None
    role_id: int | None = None
    organization_id: int | None = None
    is_active: bool | None = None
    auth_provider: str | None = None
    external_id: str | None = None
    is_local_auth_allowed: bool | None = None
    must_change_password: bool | None = None


class UserResetPasswordRequest(BaseModel):
    new_password: str
    must_change_password: bool = True


class RoleCreate(BaseModel):
    code: str
    name: str
    description: str | None = None


class RoleUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    description: str | None = None
