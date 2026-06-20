from collections import Counter
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.cmdb import CmdbApplication, CmdbAsset, CmdbDatabase, CmdbNetworkDevice
from app.models.level_profile import LevelProfile


def norm(value: str | None, default: str = "") -> str:
    return (value or default).strip().upper()


def cmdb_dashboard(db: Session) -> dict:
    assets = db.scalars(select(CmdbAsset)).all()
    apps = db.scalars(select(CmdbApplication)).all()
    dbs = db.scalars(select(CmdbDatabase)).all()
    devices = db.scalars(select(CmdbNetworkDevice)).all()
    return {
        "total_assets": len(assets),
        "total_applications": len(apps),
        "total_databases": len(dbs),
        "total_network_devices": len(devices),
        "by_asset_type": dict(Counter([a.asset_type for a in assets])),
        "by_environment": dict(Counter([a.environment or "UNKNOWN" for a in assets])),
        "by_criticality": dict(Counter([a.criticality for a in assets])),
        "unmapped_assets": sum(1 for a in assets if not a.information_system_id),
        "internet_exposed_applications": sum(1 for a in apps if a.internet_exposed),
        "sensitive_databases": sum(1 for d in dbs if d.contains_personal_data or d.contains_financial_data),
    }


def profile_inventory(db: Session, profile_id: int) -> dict:
    profile = db.get(LevelProfile, profile_id)
    if not profile:
        raise ValueError("Profile not found")
    system_id = profile.information_system_id
    assets = db.scalars(select(CmdbAsset).where(CmdbAsset.information_system_id == system_id).order_by(CmdbAsset.asset_type, CmdbAsset.asset_name)).all()
    apps = db.scalars(select(CmdbApplication).where(CmdbApplication.information_system_id == system_id).order_by(CmdbApplication.app_name)).all()
    dbs = db.scalars(select(CmdbDatabase).where(CmdbDatabase.information_system_id == system_id).order_by(CmdbDatabase.db_name)).all()
    devices = db.scalars(select(CmdbNetworkDevice).where(CmdbNetworkDevice.information_system_id == system_id).order_by(CmdbNetworkDevice.device_type, CmdbNetworkDevice.device_name)).all()
    warnings = []
    if not assets:
        warnings.append("Chưa có máy chủ/tài sản hạ tầng gắn với hồ sơ.")
    if not apps:
        warnings.append("Chưa có ứng dụng gắn với hồ sơ.")
    if not dbs:
        warnings.append("Chưa có CSDL gắn với hồ sơ.")
    if not devices:
        warnings.append("Chưa có thiết bị mạng/bảo mật gắn với hồ sơ.")
    if any(a.internet_exposed for a in apps) and not any(d.internet_edge for d in devices):
        warnings.append("Ứng dụng có kết nối Internet nhưng chưa có thiết bị biên Internet được khai báo.")
    if any(d.contains_personal_data or d.contains_financial_data for d in dbs):
        warnings.append("Hồ sơ có CSDL chứa dữ liệu cá nhân/tài chính, cần thuyết minh biện pháp bảo vệ dữ liệu.")
    return {
        "profile_id": profile_id,
        "information_system_id": system_id,
        "assets": assets,
        "applications": apps,
        "databases": dbs,
        "network_devices": devices,
        "warnings": warnings,
    }


def sync_profile_from_cmdb(db: Session, profile_id: int) -> dict:
    profile = db.get(LevelProfile, profile_id)
    if not profile:
        raise ValueError("Profile not found")
    inv = profile_inventory(db, profile_id)
    assets = inv["assets"]
    apps = inv["applications"]
    dbs = inv["databases"]
    devices = inv["network_devices"]
    scope_lines = [
        f"Ứng dụng: {len(apps)}",
        f"Máy chủ/tài sản hạ tầng: {len(assets)}",
        f"CSDL: {len(dbs)}",
        f"Thiết bị mạng/bảo mật: {len(devices)}",
    ]
    architecture_lines = []
    if apps:
        architecture_lines.append("Ứng dụng: " + ", ".join([a.app_name for a in apps[:10]]))
    if assets:
        architecture_lines.append("Máy chủ/tài sản: " + ", ".join([a.asset_name for a in assets[:10]]))
    if dbs:
        architecture_lines.append("CSDL: " + ", ".join([d.db_name for d in dbs[:10]]))
    if devices:
        architecture_lines.append("Thiết bị mạng/bảo mật: " + ", ".join([d.device_name for d in devices[:10]]))

    generated_scope = "\n".join(scope_lines)
    generated_architecture = "\n".join(architecture_lines) or "Chưa có dữ liệu CMDB để sinh kiến trúc."
    profile.system_scope_description = (profile.system_scope_description or "") + "\n\n[CMDB Sync]\n" + generated_scope
    profile.technical_architecture = (profile.technical_architecture or "") + "\n\n[CMDB Sync]\n" + generated_architecture
    db.commit()
    return {
        "profile_id": profile_id,
        "information_system_id": profile.information_system_id,
        "asset_count": len(assets),
        "application_count": len(apps),
        "database_count": len(dbs),
        "network_device_count": len(devices),
        "generated_scope": generated_scope,
        "generated_architecture": generated_architecture,
        "warnings": inv["warnings"],
    }


def import_assets(db: Session, payload: dict) -> dict:
    asset_type = norm(payload.get("asset_type"), "SERVER")
    created = 0
    updated = 0
    for row in payload.get("items", []):
        code = row.get("asset_code") or row.get("code")
        if not code:
            continue
        item = db.scalar(select(CmdbAsset).where(CmdbAsset.asset_code == code))
        data = {
            "asset_code": code,
            "asset_name": row.get("asset_name") or row.get("name") or code,
            "asset_type": row.get("asset_type") or asset_type,
            "environment": row.get("environment"),
            "ip_address": row.get("ip_address"),
            "hostname": row.get("hostname"),
            "operating_system": row.get("operating_system"),
            "information_system_id": row.get("information_system_id"),
            "criticality": row.get("criticality") or "MEDIUM",
            "status": row.get("status") or "ACTIVE",
            "description": row.get("description"),
        }
        if item:
            for k, v in data.items():
                setattr(item, k, v)
            updated += 1
        else:
            db.add(CmdbAsset(**data))
            created += 1
    db.commit()
    return {"status": "ok", "created": created, "updated": updated}
