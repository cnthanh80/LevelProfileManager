from __future__ import annotations

import csv
import io
import json
from datetime import date, datetime
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.assessment_portal import AssessmentCase
from app.models.compliance_monitoring import ComplianceMonitoringFinding, ComplianceSnapshot
from app.models.enterprise_reporting import DataWarehouseMetric, EnterpriseReportSnapshot, ReportExportJob
from app.models.information_system import InformationSystem
from app.models.level_profile import LevelProfile
from app.models.periodic_review import PeriodicReview


def _count(db: Session, stmt):
    return int(db.scalar(stmt) or 0)


def _period_label() -> str:
    today = date.today()
    return f"{today.year}-{today.month:02d}"


def calculate_enterprise_summary(db: Session) -> dict:
    total_systems = _count(db, select(func.count(InformationSystem.id)))
    total_profiles = _count(db, select(func.count(LevelProfile.id)))
    level_distribution = {}
    for level in range(1, 6):
        level_distribution[str(level)] = _count(db, select(func.count(LevelProfile.id)).where(LevelProfile.proposed_level == level))

    latest_scores = db.scalars(
        select(ComplianceSnapshot).order_by(ComplianceSnapshot.snapshot_at.desc(), ComplianceSnapshot.id.desc()).limit(200)
    ).all()
    if latest_scores:
        portfolio_average_score = round(sum(x.overall_score for x in latest_scores) / len(latest_scores))
    else:
        portfolio_average_score = 0
    high_risk_count = _count(db, select(func.count(ComplianceSnapshot.id)).where(ComplianceSnapshot.risk_level.in_(["HIGH", "CRITICAL"])))
    overdue_review_count = _count(db, select(func.count(PeriodicReview.id)).where(PeriodicReview.status.in_(["OVERDUE", "DUE"])))
    open_findings_count = _count(db, select(func.count(ComplianceMonitoringFinding.id)).where(ComplianceMonitoringFinding.status == "OPEN"))
    assessment_cases_count = _count(db, select(func.count(AssessmentCase.id)))
    latest_snapshot = db.scalars(select(EnterpriseReportSnapshot).order_by(EnterpriseReportSnapshot.generated_at.desc()).limit(1)).first()

    recommendations = []
    if high_risk_count:
        recommendations.append("Ưu tiên xử lý các hồ sơ có rủi ro cao hoặc điểm tuân thủ thấp.")
    if open_findings_count:
        recommendations.append("Phân công cán bộ xử lý các phát hiện Compliance Monitoring còn mở.")
    if overdue_review_count:
        recommendations.append("Rà soát các hồ sơ đến hạn hoặc quá hạn rà soát định kỳ.")
    if not recommendations:
        recommendations.append("Danh mục hồ sơ đang ở trạng thái ổn định, tiếp tục duy trì giám sát định kỳ.")

    return {
        "total_systems": total_systems,
        "total_profiles": total_profiles,
        "level_distribution": level_distribution,
        "portfolio_average_score": portfolio_average_score,
        "high_risk_count": high_risk_count,
        "overdue_review_count": overdue_review_count,
        "open_findings_count": open_findings_count,
        "assessment_cases_count": assessment_cases_count,
        "latest_snapshot": latest_snapshot,
        "recommendations": recommendations,
    }


def generate_enterprise_snapshot(db: Session, period_type: str = "MONTHLY", period_label: str | None = None, refresh_metrics: bool = True) -> EnterpriseReportSnapshot:
    period_label = period_label or _period_label()
    summary = calculate_enterprise_summary(db)
    code = f"ER-{period_type.upper()}-{period_label}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    snapshot = EnterpriseReportSnapshot(
        snapshot_code=code,
        period_type=period_type.upper(),
        period_label=period_label,
        total_systems=summary["total_systems"],
        total_profiles=summary["total_profiles"],
        level_1_count=summary["level_distribution"].get("1", 0),
        level_2_count=summary["level_distribution"].get("2", 0),
        level_3_count=summary["level_distribution"].get("3", 0),
        level_4_count=summary["level_distribution"].get("4", 0),
        level_5_count=summary["level_distribution"].get("5", 0),
        overall_compliance_score=summary["portfolio_average_score"],
        high_risk_count=summary["high_risk_count"],
        overdue_review_count=summary["overdue_review_count"],
        open_findings_count=summary["open_findings_count"],
        assessment_cases_count=summary["assessment_cases_count"],
        generated_at=datetime.utcnow(),
        payload_json=json.dumps({k: v for k, v in summary.items() if k != "latest_snapshot"}, ensure_ascii=False),
    )
    db.add(snapshot)
    db.flush()
    if refresh_metrics:
        refresh_data_warehouse_metrics(db, summary)
    db.commit()
    db.refresh(snapshot)
    return snapshot


def refresh_data_warehouse_metrics(db: Session, summary: dict | None = None) -> list[DataWarehouseMetric]:
    summary = summary or calculate_enterprise_summary(db)
    now = datetime.utcnow()
    metrics = [
        ("TOTAL_SYSTEMS", "PORTFOLIO", "Tổng số hệ thống thông tin", summary["total_systems"], None, None),
        ("TOTAL_PROFILES", "PORTFOLIO", "Tổng số hồ sơ cấp độ", summary["total_profiles"], None, None),
        ("AVG_COMPLIANCE_SCORE", "COMPLIANCE", "Điểm tuân thủ trung bình", summary["portfolio_average_score"], None, None),
        ("HIGH_RISK_PROFILES", "RISK", "Số hồ sơ rủi ro cao", summary["high_risk_count"], None, None),
        ("OPEN_FINDINGS", "COMPLIANCE", "Số phát hiện còn mở", summary["open_findings_count"], None, None),
        ("OVERDUE_REVIEWS", "REVIEW", "Hồ sơ đến hạn/quá hạn rà soát", summary["overdue_review_count"], None, None),
    ]
    for level, value in summary["level_distribution"].items():
        metrics.append((f"LEVEL_{level}_PROFILES", "LEVEL", f"Hồ sơ cấp độ {level}", value, "level", level))
    created = []
    for code, group, name, value, dkey, dval in metrics:
        item = DataWarehouseMetric(
            metric_code=code,
            metric_group=group,
            metric_name=name,
            metric_value=int(value or 0),
            dimension_key=dkey,
            dimension_value=str(dval) if dval is not None else None,
            measured_at=now,
        )
        db.add(item)
        created.append(item)
    db.flush()
    return created


def reporting_dashboard(db: Session) -> dict:
    summary = calculate_enterprise_summary(db)
    recent_snapshots = db.scalars(select(EnterpriseReportSnapshot).order_by(EnterpriseReportSnapshot.generated_at.desc()).limit(10)).all()
    metrics = db.scalars(select(DataWarehouseMetric).order_by(DataWarehouseMetric.measured_at.desc(), DataWarehouseMetric.id.desc()).limit(30)).all()
    board_pack = {
        "title": "Enterprise Reporting & Data Warehouse",
        "generated_at": datetime.utcnow().isoformat(),
        "kpis": {
            "systems": summary["total_systems"],
            "profiles": summary["total_profiles"],
            "average_score": summary["portfolio_average_score"],
            "high_risk": summary["high_risk_count"],
        },
        "recommendations": summary["recommendations"],
    }
    return {"summary": summary, "recent_snapshots": recent_snapshots, "data_warehouse_metrics": metrics, "board_pack": board_pack}


def portfolio_csv(db: Session, requested_by: int | None = None) -> str:
    rows = db.scalars(select(LevelProfile).order_by(LevelProfile.id)).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["profile_id", "profile_code", "system_id", "proposed_level", "status", "created_at"])
    for p in rows:
        writer.writerow([p.id, p.profile_code, p.information_system_id, p.proposed_level, p.status, p.created_at.isoformat() if p.created_at else ""])
    job = ReportExportJob(
        job_code=f"EXP-PORTFOLIO-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        report_type="PORTFOLIO_SUMMARY",
        export_format="CSV",
        status="COMPLETED",
        requested_by=requested_by,
        generated_at=datetime.utcnow(),
    )
    db.add(job)
    db.commit()
    return output.getvalue()
