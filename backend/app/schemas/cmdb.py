from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class CmdbAssetBase(BaseModel):
    asset_code: str
    asset_name: str
    asset_type: str = "SERVER"
    environment: str | None = None
    ip_address: str | None = None
    hostname: str | None = None
    operating_system: str | None = None
    owner_org_id: int | None = None
    information_system_id: int | None = None
    criticality: str = "MEDIUM"
    status: str = "ACTIVE"
    description: str | None = None


class CmdbAssetCreate(CmdbAssetBase):
    pass


class CmdbAssetUpdate(BaseModel):
    asset_name: str | None = None
    asset_type: str | None = None
    environment: str | None = None
    ip_address: str | None = None
    hostname: str | None = None
    operating_system: str | None = None
    owner_org_id: int | None = None
    information_system_id: int | None = None
    criticality: str | None = None
    status: str | None = None
    description: str | None = None


class CmdbAssetRead(CmdbAssetBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


class CmdbApplicationBase(BaseModel):
    app_code: str
    app_name: str
    information_system_id: int | None = None
    owner_org_id: int | None = None
    app_type: str = "BUSINESS"
    technology_stack: str | None = None
    internet_exposed: bool = False
    has_api: bool = False
    status: str = "ACTIVE"
    description: str | None = None


class CmdbApplicationCreate(CmdbApplicationBase):
    pass


class CmdbApplicationUpdate(BaseModel):
    app_name: str | None = None
    information_system_id: int | None = None
    owner_org_id: int | None = None
    app_type: str | None = None
    technology_stack: str | None = None
    internet_exposed: bool | None = None
    has_api: bool | None = None
    status: str | None = None
    description: str | None = None


class CmdbApplicationRead(CmdbApplicationBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


class CmdbDatabaseBase(BaseModel):
    db_code: str
    db_name: str
    information_system_id: int | None = None
    asset_id: int | None = None
    db_type: str = "ORACLE"
    data_classification: str = "INTERNAL"
    contains_personal_data: bool = False
    contains_financial_data: bool = False
    size_gb: int | None = Field(default=None, ge=0)
    status: str = "ACTIVE"
    description: str | None = None


class CmdbDatabaseCreate(CmdbDatabaseBase):
    pass


class CmdbDatabaseUpdate(BaseModel):
    db_name: str | None = None
    information_system_id: int | None = None
    asset_id: int | None = None
    db_type: str | None = None
    data_classification: str | None = None
    contains_personal_data: bool | None = None
    contains_financial_data: bool | None = None
    size_gb: int | None = Field(default=None, ge=0)
    status: str | None = None
    description: str | None = None


class CmdbDatabaseRead(CmdbDatabaseBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


class CmdbNetworkDeviceBase(BaseModel):
    device_code: str
    device_name: str
    information_system_id: int | None = None
    device_type: str = "SWITCH"
    zone: str | None = None
    ip_address: str | None = None
    ha_enabled: bool = False
    internet_edge: bool = False
    status: str = "ACTIVE"
    description: str | None = None


class CmdbNetworkDeviceCreate(CmdbNetworkDeviceBase):
    pass


class CmdbNetworkDeviceUpdate(BaseModel):
    device_name: str | None = None
    information_system_id: int | None = None
    device_type: str | None = None
    zone: str | None = None
    ip_address: str | None = None
    ha_enabled: bool | None = None
    internet_edge: bool | None = None
    status: str | None = None
    description: str | None = None


class CmdbNetworkDeviceRead(CmdbNetworkDeviceBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


class CmdbRelationshipCreate(BaseModel):
    source_type: str
    source_id: int
    target_type: str
    target_id: int
    relationship_type: str = "DEPENDS_ON"
    description: str | None = None


class CmdbRelationshipRead(CmdbRelationshipCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


class CmdbImportPayload(BaseModel):
    asset_type: str = "SERVER"
    items: list[dict]


class CmdbDashboard(BaseModel):
    total_assets: int
    total_applications: int
    total_databases: int
    total_network_devices: int
    by_asset_type: dict[str, int]
    by_environment: dict[str, int]
    by_criticality: dict[str, int]
    unmapped_assets: int
    internet_exposed_applications: int
    sensitive_databases: int


class CmdbProfileInventory(BaseModel):
    profile_id: int
    information_system_id: int
    assets: list[CmdbAssetRead]
    applications: list[CmdbApplicationRead]
    databases: list[CmdbDatabaseRead]
    network_devices: list[CmdbNetworkDeviceRead]
    warnings: list[str]


class CmdbSyncResult(BaseModel):
    profile_id: int
    information_system_id: int
    asset_count: int
    application_count: int
    database_count: int
    network_device_count: int
    generated_scope: str
    generated_architecture: str
    warnings: list[str]
