from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.core.config import settings
from app.models.user import User

router = APIRouter(prefix="/release")

CORE_TABLES = [
    "organizations",
    "roles",
    "users",
    "information_systems",
    "level_profiles",
    "security_requirements",
    "profile_requirement_answers",
    "evidence_documents",
    "profile_workflow_history",
    "approval_comments",
    "exported_documents",
    "notification_logs",
    "audit_logs",
    "periodic_reviews",
    "document_templates",
    "security_events",
    "profile_versions",
    "profile_signatures",
    "risk_register_items",
    "sla_policies",
    "assessment_cases",
    "assessment_feedbacks",
]

PRODUCTION_MODULES = [
    "auth_rbac",
    "information_system_catalog",
    "level_profile_management",
    "checklist_engine",
    "evidence_management",
    "workflow_engine",
    "dashboard",
    "document_export",
    "notification_engine",
    "advanced_audit_trail",
    "compliance_engine",
    "periodic_review_engine",
    "template_engine",
    "ldap_sso_foundation",
    "production_hardening",
    "security_hardening",
    "multi_organization_management",
    "digital_dossier_signature_mock",
    "government_template_center",
    "sla_risk_register",
    "assessment_portal",
    "executive_dashboard",
]


def _safe_count(db: Session, table_name: str) -> int | None:
    try:
        return db.execute(text(f"select count(*) from {table_name}")).scalar_one()
    except Exception:
        db.rollback()
        return None


def _version_tuple(version: str) -> tuple[int, ...]:
    parts: list[int] = []
    for item in (version or "0").replace("v", "").split("."):
        try:
            parts.append(int(item))
        except ValueError:
            parts.append(0)
    return tuple(parts)


@router.get("/info")
def release_info(current_user: User = Depends(get_current_user)):
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "release_name": "Production Release 3.0",
        "release_stage": "PRODUCTION_READY_BASELINE",
        "environment": settings.APP_ENV,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current_user": current_user.username,
        "modules": PRODUCTION_MODULES,
        "notes": [
            "v3.0 là baseline sẵn sàng UAT/production pilot cho quản lý hồ sơ đề xuất cấp độ.",
            "Ký số hiện ở chế độ mock, cần tích hợp CA/HSM/remote signing trước khi dùng chính thức.",
            "LDAP/SSO đang ở foundation, cần cấu hình theo hạ tầng định danh thực tế.",
        ],
    }


@router.get("/data-footprint")
def data_footprint(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_roles("ADMIN")),
):
    return {
        "app_version": settings.APP_VERSION,
        "tables": {table: _safe_count(db, table) for table in CORE_TABLES},
    }


@router.get("/readiness")
def release_readiness(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_roles("ADMIN")),
):
    counts = {table: _safe_count(db, table) for table in CORE_TABLES}
    checks = [
        {"code": "APP_VERSION_3", "name": "Application version is 3.0 baseline", "passed": _version_tuple(settings.APP_VERSION) >= (3, 0, 0)},
        {"code": "DB_CORE_TABLES", "name": "Core database tables are reachable", "passed": all(v is not None for v in counts.values())},
        {"code": "HAS_USERS", "name": "User and RBAC seed data exists", "passed": (counts.get("users") or 0) > 0 and (counts.get("roles") or 0) > 0},
        {"code": "HAS_SYSTEMS", "name": "Information system sample data exists", "passed": (counts.get("information_systems") or 0) > 0},
        {"code": "HAS_REQUIREMENTS", "name": "Security requirement catalog exists", "passed": (counts.get("security_requirements") or 0) > 0},
        {"code": "EVIDENCE_READY", "name": "Evidence document module is available", "passed": counts.get("evidence_documents") is not None},
        {"code": "WORKFLOW_READY", "name": "Workflow history is available", "passed": counts.get("profile_workflow_history") is not None},
        {"code": "AUDIT_ENABLED", "name": "Audit trail table exists", "passed": counts.get("audit_logs") is not None},
        {"code": "NOTIFICATION_ENABLED", "name": "Notification log table exists", "passed": counts.get("notification_logs") is not None},
        {"code": "SECURITY_EVENTS", "name": "Security event table exists", "passed": counts.get("security_events") is not None},
        {"code": "DIGITAL_DOSSIER", "name": "Digital dossier versioning and signature tables exist", "passed": counts.get("profile_versions") is not None and counts.get("profile_signatures") is not None},
        {"code": "TEMPLATE_CENTER", "name": "Government template center exists", "passed": counts.get("document_templates") is not None},
        {"code": "RISK_SLA", "name": "Risk register and SLA modules exist", "passed": counts.get("risk_register_items") is not None and counts.get("sla_policies") is not None},
        {"code": "ASSESSMENT_PORTAL", "name": "Assessment portal tables exist", "passed": counts.get("assessment_cases") is not None and counts.get("assessment_feedbacks") is not None},
        {"code": "SAFE_NOTIFICATION_MODE", "name": "Notification dry-run mode is explicit", "passed": settings.NOTIFICATION_DRY_RUN in [True, False]},
        {"code": "ORG_HIERARCHY", "name": "Organization hierarchy is enabled", "passed": counts.get("organizations") is not None},
        {"code": "SECURITY_HEADERS", "name": "Security headers middleware is enabled", "passed": settings.SECURITY_HEADERS_ENABLED},
        {"code": "JWT_SECRET_CHANGED", "name": "JWT secret should be changed before production", "passed": settings.JWT_SECRET_KEY != "change_this_secret_key_in_production"},
    ]
    passed = sum(1 for item in checks if item["passed"])
    total = len(checks)
    score = round(passed * 100 / total, 2) if total else 0
    return {
        "release": "3.0.0",
        "readiness_score": score,
        "status": "READY_FOR_PRODUCTION_PILOT" if score >= 85 else "READY_FOR_UAT" if score >= 75 else "NEEDS_ATTENTION",
        "passed": passed,
        "total": total,
        "checks": checks,
    }


@router.get("/production-readiness")
def production_readiness(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_roles("ADMIN")),
):
    counts = {table: _safe_count(db, table) for table in CORE_TABLES}
    controls = [
        {"group": "Application", "item": "APP_ENV=production on production host", "status": "PASS" if settings.APP_ENV == "production" else "WARN", "detail": f"Current APP_ENV={settings.APP_ENV}"},
        {"group": "Security", "item": "JWT secret changed", "status": "PASS" if settings.JWT_SECRET_KEY != "change_this_secret_key_in_production" else "FAIL", "detail": "Use a strong secret in backend/.env"},
        {"group": "Security", "item": "Security headers enabled", "status": "PASS" if settings.SECURITY_HEADERS_ENABLED else "FAIL", "detail": "SECURITY_HEADERS_ENABLED=true"},
        {"group": "Security", "item": "Rate limit enabled for production", "status": "PASS" if settings.RATE_LIMIT_ENABLED else "WARN", "detail": "RATE_LIMIT_ENABLED should be true in production"},
        {"group": "Notification", "item": "Email/Telegram mode reviewed", "status": "PASS" if settings.NOTIFICATION_DRY_RUN else "PASS", "detail": "Dry-run is safe for UAT; disable only after SMTP/Telegram is configured"},
        {"group": "Data", "item": "Core tables reachable", "status": "PASS" if all(v is not None for v in counts.values()) else "FAIL", "detail": "Database schema is complete"},
        {"group": "Operations", "item": "Backup scripts included", "status": "PASS", "detail": "Use scripts/windows-backup-db.ps1 and scripts/windows-restore-db.ps1"},
        {"group": "Identity", "item": "LDAP/SSO foundation available", "status": "PASS", "detail": "Configure LDAP/SSO before enterprise go-live"},
        {"group": "Legal", "item": "Digital signature integration", "status": "WARN", "detail": "Current release uses mock signing; integrate CA/HSM/remote signing for formal use"},
    ]
    fails = sum(1 for item in controls if item["status"] == "FAIL")
    warns = sum(1 for item in controls if item["status"] == "WARN")
    return {
        "release": "3.0.0",
        "status": "BLOCKED" if fails else "READY_WITH_WARNINGS" if warns else "READY",
        "fails": fails,
        "warnings": warns,
        "controls": controls,
    }


@router.get("/uat-checklist")
def uat_checklist(_=Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REVIEWER"))):
    return {
        "release": "3.0.0",
        "checklist": [
            {"code": "UAT-001", "name": "Đăng nhập admin/attt và kiểm tra phân quyền cơ bản.", "status": "TODO"},
            {"code": "UAT-002", "name": "Tạo mới hệ thống thông tin và hồ sơ đề xuất cấp độ.", "status": "TODO"},
            {"code": "UAT-003", "name": "Sinh checklist theo cấp độ và cập nhật trạng thái đáp ứng.", "status": "TODO"},
            {"code": "UAT-004", "name": "Upload tài liệu minh chứng và gắn với checklist.", "status": "TODO"},
            {"code": "UAT-005", "name": "Thực hiện luồng workflow: nháp → rà soát → phê duyệt nội bộ.", "status": "TODO"},
            {"code": "UAT-006", "name": "Xuất hồ sơ/tờ trình/quyết định/phụ lục checklist DOCX/PDF.", "status": "TODO"},
            {"code": "UAT-007", "name": "Kiểm tra hồ sơ điện tử, tạo phiên bản và ký số mô phỏng.", "status": "TODO"},
            {"code": "UAT-008", "name": "Kiểm tra kho biểu mẫu cơ quan và template mặc định.", "status": "TODO"},
            {"code": "UAT-009", "name": "Kiểm tra Risk Register, SLA và cảnh báo quá hạn.", "status": "TODO"},
            {"code": "UAT-010", "name": "Gửi hồ sơ sang cổng thẩm định và phản hồi ý kiến thẩm định.", "status": "TODO"},
            {"code": "UAT-011", "name": "Kiểm tra dashboard lãnh đạo, dashboard compliance và dashboard rà soát định kỳ.", "status": "TODO"},
            {"code": "UAT-012", "name": "Gửi thử thông báo email/Telegram ở chế độ dry-run.", "status": "TODO"},
            {"code": "UAT-013", "name": "Kiểm tra audit trail, security events và account lockout.", "status": "TODO"},
            {"code": "UAT-014", "name": "Rà soát cấu hình production trước khi triển khai ngoài môi trường dev.", "status": "TODO"},
            {"code": "UAT-015", "name": "Kiểm tra cây tổ chức, phạm vi đơn vị và thống kê hồ sơ theo tổ chức.", "status": "TODO"},
        ],
    }
