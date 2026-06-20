from datetime import datetime
from pydantic import BaseModel, Field


class SignatureProviderCreate(BaseModel):
    code: str = Field(..., max_length=50)
    name: str
    provider_type: str = "REMOTE_SIGNING"
    status: str = "ACTIVE"
    endpoint_url: str | None = None
    callback_url: str | None = None
    description: str | None = None
    config_json: str | None = None


class SignatureProviderUpdate(BaseModel):
    name: str | None = None
    provider_type: str | None = None
    status: str | None = None
    endpoint_url: str | None = None
    callback_url: str | None = None
    description: str | None = None
    config_json: str | None = None


class SignatureProviderRead(BaseModel):
    id: int
    code: str
    name: str
    provider_type: str
    status: str
    endpoint_url: str | None = None
    callback_url: str | None = None
    description: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RealSignRequestCreate(BaseModel):
    provider_id: int | None = None
    sign_method: str = "REMOTE_SIGNING"
    signer_name: str | None = None
    signer_role: str | None = None
    callback_url: str | None = None
    note: str | None = None


class SignatureCallbackPayload(BaseModel):
    status: str = "SIGNED"
    external_transaction_id: str | None = None
    signed_hash: str | None = None
    certificate_subject: str | None = None
    signer_name: str | None = None
    signer_role: str | None = None
    error_message: str | None = None
    raw_payload: dict | None = None


class SignatureRequestRead(BaseModel):
    id: int
    profile_id: int
    version_id: int
    provider_id: int | None = None
    requested_by: int | None = None
    request_code: str
    sign_method: str
    status: str
    document_hash: str
    external_transaction_id: str | None = None
    signed_hash: str | None = None
    signed_file_path: str | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SignatureGatewayStatus(BaseModel):
    providers_total: int
    active_providers: int
    requests_total: int
    pending_requests: int
    signed_requests: int
    failed_requests: int
    supported_methods: list[str]
    production_note: str
