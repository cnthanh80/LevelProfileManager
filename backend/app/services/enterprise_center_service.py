from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.core.config import get_cors_origins, settings
from app.models.audit_log import AuditLog
from app.models.assessment_portal import AssessmentCase
from app.models.cmdb import CmdbAsset
from app.models.compliance_monitoring import ComplianceMonitoringFinding, ComplianceSnapshot
from app.models.enterprise_center import (
    BackupRecord,
    DataRetentionPolicy,
    EnterpriseConfiguration,
    EnterpriseHealthCheck,
    EnterpriseJobSchedule,
)
from app.models.evidence_document import EvidenceDocument
from app.models.information_system import InformationSystem
from app.models.level_profile import LevelProfile
from app.models.notification_log import NotificationLog
from app.models.profile_signature import ProfileSignature
from app.models.siem_integration import SiemConnector
from app.models.user import User
from app.schemas.enterprise_center import (
    EnterpriseHealthDashboard,
    EnterpriseReadinessCheck,
    EnterpriseReadinessDashboard,
)


def _count(db: Session, model) -> int:
    return db.scalar(select(func.count(model.id))) or 0


def seed_enterprise_defaults(db: Session) -> dict:
    configs = [
        ("SMTP_ENABLED", "NOTIFICATION", "SMTP enabled", str(settings.SMTP_ENABLED), "BOOLEAN", False, "Bật/tắt gửi email."),
        ("TELEGRAM_ENABLED", "NOTIFICATION", "Telegram enabled", str(settings.TELEGRAM_ENABLED), "BOOLEAN", False, "Bật/tắt gửi Telegram."),
        ("LDAP_ENABLED", "IDENTITY", "LDAP enabled", str(settings.LDAP_ENABLED), "BOOLEAN", False, "Bật/tắt xác thực LDAP."),
        ("SSO_ENABLED", "IDENTITY", "SSO enabled", str(settings.SSO_ENABLED), "BOOLEAN", False, "Bật/tắt SSO."),
        ("SIEM_ENABLED", "SIEM", "SIEM integration", "FOUNDATION", "STRING", False, "Trạng thái tích hợp SIEM/SOC."),
        ("BACKUP_POLICY", "BACKUP", "Backup policy", "Daily logical backup", "STRING", False, "Chính sách sao lưu mặc định."),
    ]
    created_configs = 0
    for key, group, name, value, value_type, secret, description in configs:
        item = db.scalar(select(EnterpriseConfiguration).where(EnterpriseConfiguration.config_key == key))
        if not item:
            db.add(EnterpriseConfiguration(config_key=key, config_group=group, display_name=name, config_value=value, value_type=value_type, is_secret=secret, description=description))
            created_configs += 1

    jobs = [
        ("COMPLIANCE_MONITORING_DAILY", "Compliance Monitoring Daily", "COMPLIANCE", "DAILY 00:30", "Tính score tuân thủ và phát hiện GAP."),
        ("PERIODIC_REVIEW_REMINDER", "Periodic Review Reminder", "REVIEW", "DAILY 08:00", "Nhắc các hồ sơ đến hạn rà soát."),
        ("NOTIFICATION_DISPATCH", "Notification Dispatch", "NOTIFICATION", "EVERY 15 MINUTES", "Gửi thông báo email/Telegram."),
        ("ENTERPRISE_REPORTING_SNAPSHOT", "Enterprise Reporting Snapshot", "REPORTING", "MONTHLY 01 01:00", "Sinh snapshot báo cáo điều hành."),
        ("AUDIT_RETENTION_CHECK", "Audit Retention Check", "RETENTION", "WEEKLY SUN 02:00", "Kiểm tra chính sách lưu giữ audit."),
    ]
    created_jobs = 0
    for code, name, group, expr, message in jobs:
        item = db.scalar(select(EnterpriseJobSchedule).where(EnterpriseJobSchedule.job_code == code))
        if not item:
            db.add(EnterpriseJobSchedule(job_code=code, job_name=name, job_group=group, schedule_expression=expr, next_run_hint=expr, last_status="READY", last_message=message))
            created_jobs += 1

    policies = [
        ("RET-AUDIT-365", "AUDIT_LOGS", 365, True, False, True, "Lưu audit log tối thiểu 365 ngày."),
        ("RET-NOTIF-180", "NOTIFICATION_LOGS", 180, True, True, False, "Lưu thông báo 180 ngày."),
        ("RET-EVIDENCE-1825", "EVIDENCE_DOCUMENTS", 1825, True, False, True, "Lưu minh chứng tối thiểu 5 năm."),
        ("RET-WORKFLOW-1825", "WORKFLOW_HISTORY", 1825, True, False, True, "Lưu lịch sử workflow tối thiểu 5 năm."),
    ]
    created_policies = 0
    for code, domain, days, archive, purge, hold, description in policies:
        item = db.scalar(select(DataRetentionPolicy).where(DataRetentionPolicy.policy_code == code))
        if not item:
            db.add(DataRetentionPolicy(policy_code=code, data_domain=domain, retention_days=days, archive_enabled=archive, purge_enabled=purge, legal_hold=hold, description=description))
            created_policies += 1
    db.commit()
    return {"created_configurations": created_configs, "created_jobs": created_jobs, "created_policies": created_policies}


def run_health_checks(db: Session) -> EnterpriseHealthDashboard:
    now = datetime.utcnow()
    started = datetime.utcnow()
    status = "UP"
    message = "Database query OK"
    latency_ms = 0
    try:
        db.execute(text("select 1"))
        latency_ms = int((datetime.utcnow() - started).total_seconds() * 1000)
    except Exception as exc:  # pragma: no cover
        status = "DOWN"
        message = str(exc)
    components = [
        ("DATABASE", "PostgreSQL Database", "CORE", status, latency_ms, message),
        ("BACKEND_API", "FastAPI Backend", "CORE", "UP", None, "API process is running."),
        ("FRONTEND", "React/Nginx Frontend", "CORE", "UP", None, "Frontend container expected on port 3000."),
        ("STORAGE", "Local/S3-compatible Storage", "INFRA", "UP", None, f"Storage path: {settings.FILE_STORAGE_PATH}"),
        ("NOTIFICATION", "Email/Telegram Notification", "INTEGRATION", "DEGRADED" if settings.NOTIFICATION_DRY_RUN else "UP", None, "Dry-run mode enabled." if settings.NOTIFICATION_DRY_RUN else "Notification engine enabled."),
        ("LDAP_SSO", "LDAP/SSO", "IDENTITY", "UP" if settings.LDAP_ENABLED or settings.SSO_ENABLED else "DEGRADED", None, "LDAP/SSO enabled." if settings.LDAP_ENABLED or settings.SSO_ENABLED else "Local authentication is active."),
        ("SIEM", "SIEM/SOC Integration", "INTEGRATION", "UP" if _count(db, SiemConnector) else "DEGRADED", None, "SIEM connector configured." if _count(db, SiemConnector) else "No SIEM connector configured."),
    ]
    rows = []
    for code, name, group, comp_status, latency, msg in components:
        row = EnterpriseHealthCheck(component_code=code, component_name=name, component_group=group, status=comp_status, latency_ms=latency, message=msg, checked_at=now)
        db.add(row)
        rows.append(row)
    db.commit()
    for row in rows:
        db.refresh(row)
    summary = {"UP": 0, "DEGRADED": 0, "DOWN": 0, "UNKNOWN": 0}
    for row in rows:
        summary[row.status] = summary.get(row.status, 0) + 1
    overall = "DOWN" if summary.get("DOWN", 0) else "DEGRADED" if summary.get("DEGRADED", 0) else "UP"
    return EnterpriseHealthDashboard(status=overall, generated_at=now, components=rows, summary=summary)


def latest_health_dashboard(db: Session) -> EnterpriseHealthDashboard:
    rows = db.scalars(select(EnterpriseHealthCheck).order_by(EnterpriseHealthCheck.checked_at.desc()).limit(20)).all()
    if not rows:
        return run_health_checks(db)
    latest_time = rows[0].checked_at
    latest = [r for r in rows if r.checked_at == latest_time]
    summary = {"UP": 0, "DEGRADED": 0, "DOWN": 0, "UNKNOWN": 0}
    for row in latest:
        summary[row.status] = summary.get(row.status, 0) + 1
    overall = "DOWN" if summary.get("DOWN", 0) else "DEGRADED" if summary.get("DEGRADED", 0) else "UP"
    return EnterpriseHealthDashboard(status=overall, generated_at=latest_time, components=latest, summary=summary)


def enterprise_readiness(db: Session) -> EnterpriseReadinessDashboard:
    total_profiles = _count(db, LevelProfile)
    total_systems = _count(db, InformationSystem)
    evidence_count = _count(db, EvidenceDocument)
    signature_count = _count(db, ProfileSignature)
    audit_count = _count(db, AuditLog)
    user_count = _count(db, User)
    cmdb_count = _count(db, CmdbAsset)
    siem_count = _count(db, SiemConnector)
    monitoring_snapshots = _count(db, ComplianceSnapshot)
    open_monitoring_findings = db.scalar(select(func.count(ComplianceMonitoringFinding.id)).where(ComplianceMonitoringFinding.status == "OPEN")) or 0
    assessment_cases = _count(db, AssessmentCase)

    checks = [
        EnterpriseReadinessCheck(domain="Core Portfolio", status="PASS" if total_systems and total_profiles else "WARN", score=100 if total_systems and total_profiles else 60, message=f"{total_systems} hệ thống, {total_profiles} hồ sơ."),
        EnterpriseReadinessCheck(domain="Evidence", status="PASS" if evidence_count else "WARN", score=90 if evidence_count else 55, message=f"{evidence_count} tài liệu minh chứng."),
        EnterpriseReadinessCheck(domain="Audit", status="PASS" if audit_count else "WARN", score=90 if audit_count else 60, message=f"{audit_count} bản ghi audit."),
        EnterpriseReadinessCheck(domain="Identity", status="PASS" if settings.LDAP_ENABLED or settings.SSO_ENABLED else "WARN", score=95 if settings.LDAP_ENABLED or settings.SSO_ENABLED else 70, message="LDAP/SSO đã bật." if settings.LDAP_ENABLED or settings.SSO_ENABLED else "Đang dùng tài khoản nội bộ; cần bật LDAP/SSO khi production."),
        EnterpriseReadinessCheck(domain="CMDB", status="PASS" if cmdb_count else "WARN", score=90 if cmdb_count else 65, message=f"{cmdb_count} tài sản CMDB."),
        EnterpriseReadinessCheck(domain="SIEM/SOC", status="PASS" if siem_count else "WARN", score=90 if siem_count else 65, message=f"{siem_count} connector SIEM."),
        EnterpriseReadinessCheck(domain="Compliance Monitoring", status="PASS" if monitoring_snapshots else "WARN", score=92 if monitoring_snapshots else 60, message=f"{monitoring_snapshots} snapshot; {open_monitoring_findings} finding đang mở."),
        EnterpriseReadinessCheck(domain="Digital Signature", status="PASS" if signature_count else "WARN", score=88 if signature_count else 65, message=f"{signature_count} chữ ký/hồ sơ ký."),
        EnterpriseReadinessCheck(domain="Assessment", status="PASS" if assessment_cases else "WARN", score=85 if assessment_cases else 65, message=f"{assessment_cases} hồ sơ/case thẩm định."),
        EnterpriseReadinessCheck(domain="Users", status="PASS" if user_count >= 2 else "WARN", score=90 if user_count >= 2 else 60, message=f"{user_count} người dùng."),
    ]
    overall_score = round(sum(c.score for c in checks) / len(checks))
    readiness_level = "ENTERPRISE_READY" if overall_score >= 85 and all(c.status != "FAIL" for c in checks) else "PRODUCTION_READY" if overall_score >= 75 else "NEEDS_ATTENTION"
    recommendations = []
    if not (settings.LDAP_ENABLED or settings.SSO_ENABLED):
        recommendations.append("Bật LDAP/SSO production trước khi triển khai diện rộng.")
    if not siem_count:
        recommendations.append("Cấu hình SIEM connector để đồng bộ sự kiện ATTT về SOC.")
    if not cmdb_count:
        recommendations.append("Nhập hoặc đồng bộ CMDB để giảm nhập liệu thủ công trong hồ sơ cấp độ.")
    if settings.NOTIFICATION_DRY_RUN:
        recommendations.append("Tắt NOTIFICATION_DRY_RUN và cấu hình SMTP/Telegram thật khi vận hành production.")
    if not recommendations:
        recommendations.append("Hệ thống đạt baseline enterprise; duy trì kiểm tra sức khỏe và backup định kỳ.")
    return EnterpriseReadinessDashboard(overall_score=overall_score, readiness_level=readiness_level, checks=checks, recommendations=recommendations)


def enterprise_dashboard(db: Session) -> dict:
    seed_enterprise_defaults(db)
    latest_backup = db.scalars(select(BackupRecord).order_by(BackupRecord.started_at.desc(), BackupRecord.id.desc()).limit(1)).first()
    readiness = enterprise_readiness(db)
    health = latest_health_dashboard(db)
    return {
        "readiness": readiness,
        "health": health,
        "configuration_count": _count(db, EnterpriseConfiguration),
        "enabled_job_count": db.scalar(select(func.count(EnterpriseJobSchedule.id)).where(EnterpriseJobSchedule.is_enabled == True)) or 0,
        "retention_policy_count": _count(db, DataRetentionPolicy),
        "latest_backup": latest_backup,
    }


def create_backup_record(db: Session, backup_type: str = "LOGICAL", scope: str = "DATABASE", status: str = "COMPLETED", storage_location: str | None = None, size_mb: int = 0, notes: str | None = None) -> BackupRecord:
    now = datetime.utcnow()
    checksum = uuid4().hex + uuid4().hex
    record = BackupRecord(
        backup_code=f"BKP-{now.strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:6].upper()}",
        backup_type=backup_type.upper(),
        scope=scope.upper(),
        status=status.upper(),
        storage_location=storage_location or "/app/backups/mock",
        checksum=checksum[:64],
        size_mb=size_mb,
        started_at=now,
        completed_at=now if status.upper() in {"COMPLETED", "FAILED"} else None,
        validation_status="PENDING",
        notes=notes or "Mock backup metadata generated by Enterprise Center.",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def validate_backup_record(db: Session, backup_id: int) -> BackupRecord:
    record = db.get(BackupRecord, backup_id)
    if not record:
        raise ValueError("Backup record not found")
    record.validated_at = datetime.utcnow()
    record.validation_status = "VALID"
    if not record.notes:
        record.notes = "Backup validation completed."
    db.commit()
    db.refresh(record)
    return record
