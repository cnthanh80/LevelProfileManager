from __future__ import annotations

from datetime import datetime, date
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.level_profile import LevelProfile
from app.models.risk_register import RiskRegisterItem, SlaPolicy


def calculate_risk_score(likelihood: int, impact: int) -> tuple[int, str]:
    score = max(1, min(5, likelihood)) * max(1, min(5, impact))
    if score >= 20:
        return score, "CRITICAL"
    if score >= 12:
        return score, "HIGH"
    if score >= 6:
        return score, "MEDIUM"
    return score, "LOW"


def normalize_risk(item: RiskRegisterItem) -> RiskRegisterItem:
    item.risk_score, item.risk_level = calculate_risk_score(item.likelihood, item.impact)
    item.category = (item.category or "GENERAL").upper()
    item.status = (item.status or "OPEN").upper()
    return item


def get_risk_summary(db: Session) -> dict:
    items = db.scalars(select(RiskRegisterItem)).all()
    today = date.today()
    by_level: dict[str, int] = {}
    by_status: dict[str, int] = {}
    for item in items:
        by_level[item.risk_level] = by_level.get(item.risk_level, 0) + 1
        by_status[item.status] = by_status.get(item.status, 0) + 1
    top = sorted(items, key=lambda x: (x.risk_score, x.id), reverse=True)[:10]
    return {
        "total": len(items),
        "open_items": sum(1 for x in items if x.status in {"OPEN", "IN_PROGRESS"}),
        "critical_items": sum(1 for x in items if x.risk_level == "CRITICAL"),
        "high_items": sum(1 for x in items if x.risk_level == "HIGH"),
        "overdue_items": sum(1 for x in items if x.due_date and x.due_date < today and x.status not in {"CLOSED", "ACCEPTED"}),
        "by_level": by_level,
        "by_status": by_status,
        "top_risks": top,
    }


def seed_default_sla_policies(db: Session) -> int:
    defaults = [
        {"code": "SLA_DRAFT", "name": "Hoàn thiện hồ sơ nháp", "workflow_status": "DRAFT", "severity": "MEDIUM", "due_hours": 120, "warning_hours": 24},
        {"code": "SLA_INTERNAL_REVIEW", "name": "Rà soát nội bộ", "workflow_status": "INTERNAL_REVIEW", "severity": "HIGH", "due_hours": 72, "warning_hours": 24},
        {"code": "SLA_LEADER_APPROVAL", "name": "Lãnh đạo phê duyệt", "workflow_status": "LEADER_APPROVAL", "severity": "HIGH", "due_hours": 48, "warning_hours": 12},
        {"code": "SLA_ASSESSMENT_COMMENT", "name": "Xử lý ý kiến thẩm định", "workflow_status": "ASSESSMENT_COMMENTED", "severity": "CRITICAL", "due_hours": 72, "warning_hours": 24},
    ]
    created = 0
    for data in defaults:
        existing = db.scalar(select(SlaPolicy).where(SlaPolicy.code == data["code"]))
        if existing:
            continue
        db.add(SlaPolicy(**data, target_type="WORKFLOW", is_active="Y", description="SLA mặc định cho workflow hồ sơ cấp độ"))
        created += 1
    db.commit()
    return created


def get_sla_summary(db: Session) -> dict:
    policies = db.scalars(select(SlaPolicy).where(SlaPolicy.is_active == "Y")).all()
    profiles = db.scalars(select(LevelProfile)).all()
    now = datetime.utcnow()
    items = []
    for profile in profiles:
        policy = next((p for p in policies if p.workflow_status == profile.status), None)
        if not policy:
            continue
        age_hours = int((now - profile.updated_at).total_seconds() // 3600)
        if age_hours >= policy.due_hours:
            state = "BREACHED"
        elif age_hours >= max(0, policy.due_hours - policy.warning_hours):
            state = "WARNING"
        else:
            continue
        items.append({
            "profile_id": profile.id,
            "profile_code": profile.profile_code,
            "current_status": profile.status,
            "age_hours": age_hours,
            "due_hours": policy.due_hours,
            "severity": policy.severity,
            "state": state,
        })
    return {
        "active_policies": len(policies),
        "warning_items": sum(1 for x in items if x["state"] == "WARNING"),
        "breached_items": sum(1 for x in items if x["state"] == "BREACHED"),
        "items": items,
    }
