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
    "users",
    "roles",
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
]


def _safe_count(db: Session, table_name: str) -> int | None:
    try:
        return db.execute(text(f"select count(*) from {table_name}")).scalar_one()
    except Exception:
        db.rollback()
        return None


@router.get("/info")
def release_info(current_user: User = Depends(get_current_user)):
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "release_name": "MVP Release 2.0",
        "environment": settings.APP_ENV,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current_user": current_user.username,
        "modules": [
            "auth_rbac",
            "information_system_catalog",
            "level_profile_management",
            "checklist_engine",
            "evidence_management",
            "workflow_engine",
            "dashboard",
            "document_export",
            "notification_engine",
            "audit_trail",
            "template_engine",
            "ldap_sso_foundation",
            "production_hardening",
            "security_hardening",
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
        {"code": "DB_CORE_TABLES", "name": "Core database tables are reachable", "passed": all(v is not None for v in counts.values())},
        {"code": "HAS_USERS", "name": "User and RBAC seed data exists", "passed": (counts.get("users") or 0) > 0 and (counts.get("roles") or 0) > 0},
        {"code": "HAS_SYSTEMS", "name": "Information system sample data exists", "passed": (counts.get("information_systems") or 0) > 0},
        {"code": "HAS_REQUIREMENTS", "name": "Security requirement catalog exists", "passed": (counts.get("security_requirements") or 0) > 0},
        {"code": "AUDIT_ENABLED", "name": "Audit trail table exists", "passed": counts.get("audit_logs") is not None},
        {"code": "NOTIFICATION_ENABLED", "name": "Notification log table exists", "passed": counts.get("notification_logs") is not None},
        {"code": "SECURITY_EVENTS", "name": "Security event table exists", "passed": counts.get("security_events") is not None},
        {"code": "SAFE_NOTIFICATION_MODE", "name": "Notification dry-run is enabled for local development", "passed": settings.NOTIFICATION_DRY_RUN},
    ]
    passed = sum(1 for item in checks if item["passed"])
    total = len(checks)
    score = round(passed * 100 / total, 2) if total else 0
    return {
        "release": "2.0.0",
        "readiness_score": score,
        "status": "READY_FOR_UAT" if score >= 80 else "NEEDS_ATTENTION",
        "passed": passed,
        "total": total,
        "checks": checks,
    }


@router.get("/uat-checklist")
def uat_checklist(_=Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REVIEWER"))):
    return {
        "release": "2.0.0",
        "checklist": [
            "Đăng nhập admin/attt và kiểm tra phân quyền cơ bản.",
            "Tạo mới hệ thống thông tin và hồ sơ đề xuất cấp độ.",
            "Sinh checklist theo cấp độ và cập nhật trạng thái đáp ứng.",
            "Upload tài liệu minh chứng và gắn với checklist.",
            "Thực hiện luồng workflow: nháp → rà soát → phê duyệt nội bộ.",
            "Xuất hồ sơ/tờ trình/quyết định/phụ lục checklist DOCX/PDF.",
            "Kiểm tra dashboard lãnh đạo, dashboard compliance và dashboard rà soát định kỳ.",
            "Gửi thử thông báo email/Telegram ở chế độ dry-run.",
            "Kiểm tra audit trail, security events và account lockout.",
            "Rà soát cấu hình production trước khi triển khai ngoài môi trường dev.",
        ],
    }
