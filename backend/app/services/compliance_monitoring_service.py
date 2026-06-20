from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.compliance_monitoring import (
    ComplianceMonitoringFinding,
    ComplianceMonitoringNotification,
    ComplianceSnapshot,
)
from app.models.compliance_automation import ComplianceAutomationFinding
from app.models.evidence_document import EvidenceDocument
from app.models.information_system import InformationSystem
from app.models.level_profile import LevelProfile
from app.models.organization import Organization
from app.models.profile_requirement_answer import ProfileRequirementAnswer
from app.models.security_requirement import SecurityRequirement


def _pct(part: int, total: int) -> int:
    if total <= 0:
        return 100
    return max(0, min(100, round(part * 100 / total)))


def _risk_level(score: int, mandatory_gap_count: int, open_finding_count: int) -> str:
    if score < 50 or mandatory_gap_count >= 5:
        return "CRITICAL"
    if score < 70 or mandatory_gap_count >= 2 or open_finding_count >= 5:
        return "HIGH"
    if score < 85 or mandatory_gap_count >= 1 or open_finding_count >= 1:
        return "MEDIUM"
    return "LOW"


def _heat_color(risk_level: str, score: int) -> str:
    if risk_level == "CRITICAL" or score < 50:
        return "RED"
    if risk_level == "HIGH" or score < 70:
        return "ORANGE"
    if risk_level == "MEDIUM" or score < 85:
        return "YELLOW"
    return "GREEN"


def _is_technical(req: SecurityRequirement) -> bool:
    raw = f"{req.group_name or ''} {req.category or ''}".lower()
    return any(token in raw for token in ["technical", "kỹ", "ky", "mạng", "mang", "server", "ứng dụng", "ung dung", "dữ liệu", "du lieu"])


def _system_org(db: Session, profile: LevelProfile) -> tuple[str | None, str | None]:
    system = db.get(InformationSystem, profile.information_system_id)
    if not system:
        return None, None
    org_name = None
    if system.owner_org_id:
        org = db.get(Organization, system.owner_org_id)
        org_name = org.name if org else None
    return system.name, org_name


def _latest_snapshot(db: Session, profile_id: int) -> ComplianceSnapshot | None:
    return db.scalars(
        select(ComplianceSnapshot)
        .where(ComplianceSnapshot.profile_id == profile_id)
        .order_by(ComplianceSnapshot.snapshot_at.desc(), ComplianceSnapshot.id.desc())
        .limit(1)
    ).first()


def calculate_profile_monitoring_score(db: Session, profile_id: int) -> dict:
    profile = db.get(LevelProfile, profile_id)
    if not profile:
        raise ValueError(f"Profile {profile_id} not found")

    answers = db.scalars(select(ProfileRequirementAnswer).where(ProfileRequirementAnswer.profile_id == profile_id)).all()
    req_ids = [a.requirement_id for a in answers]
    req_map: dict[int, SecurityRequirement] = {}
    if req_ids:
        reqs = db.scalars(select(SecurityRequirement).where(SecurityRequirement.id.in_(req_ids))).all()
        req_map = {r.id: r for r in reqs}

    mgmt_total = mgmt_ok = tech_total = tech_ok = 0
    mandatory_total = mandatory_ok = 0
    gap_count = 0
    missing_evidence_count = 0
    compliant_count = 0
    compliant_with_evidence = 0

    for ans in answers:
        status = (ans.status or "").upper()
        req = req_map.get(ans.requirement_id)
        is_ok = status == "COMPLIANT"
        is_gap = status == "NON_COMPLIANT"
        if req and _is_technical(req):
            tech_total += 1
            if is_ok:
                tech_ok += 1
        else:
            mgmt_total += 1
            if is_ok:
                mgmt_ok += 1
        if req and req.is_mandatory:
            mandatory_total += 1
            if is_ok:
                mandatory_ok += 1
        if is_gap:
            gap_count += 1
        if is_ok:
            compliant_count += 1
            if (ans.evidence_count or 0) > 0:
                compliant_with_evidence += 1
            else:
                missing_evidence_count += 1

    mandatory_gap_count = max(0, mandatory_total - mandatory_ok)
    management_score = _pct(mgmt_ok, mgmt_total)
    technical_score = _pct(tech_ok, tech_total)
    evidence_score = _pct(compliant_with_evidence, compliant_count)

    open_findings = db.scalar(
        select(func.count(ComplianceAutomationFinding.id)).where(
            ComplianceAutomationFinding.profile_id == profile_id,
            ComplianceAutomationFinding.status == "OPEN",
        )
    ) or 0
    critical_findings = db.scalar(
        select(func.count(ComplianceAutomationFinding.id)).where(
            ComplianceAutomationFinding.profile_id == profile_id,
            ComplianceAutomationFinding.status == "OPEN",
            ComplianceAutomationFinding.severity == "CRITICAL",
        )
    ) or 0
    high_findings = db.scalar(
        select(func.count(ComplianceAutomationFinding.id)).where(
            ComplianceAutomationFinding.profile_id == profile_id,
            ComplianceAutomationFinding.status == "OPEN",
            ComplianceAutomationFinding.severity == "HIGH",
        )
    ) or 0
    automation_penalty = critical_findings * 15 + high_findings * 8 + max(0, open_findings - critical_findings - high_findings) * 3
    automation_score = max(0, min(100, 100 - automation_penalty))

    overall_score = round(management_score * 0.30 + technical_score * 0.35 + evidence_score * 0.20 + automation_score * 0.15)
    latest = _latest_snapshot(db, profile_id)
    trend_direction = "STABLE"
    if latest:
        if overall_score <= latest.overall_score - 5:
            trend_direction = "DOWN"
        elif overall_score >= latest.overall_score + 5:
            trend_direction = "UP"
    risk_level = _risk_level(overall_score, mandatory_gap_count, open_findings)

    recommendations: list[str] = []
    if mandatory_gap_count:
        recommendations.append("Ưu tiên xử lý các tiêu chí bắt buộc chưa đáp ứng trước khi gửi thẩm định.")
    if missing_evidence_count:
        recommendations.append("Bổ sung tài liệu minh chứng cho các tiêu chí đã đánh dấu đáp ứng.")
    if open_findings:
        recommendations.append("Xem lại các phát hiện Compliance Automation đang mở và phân công người xử lý.")
    if trend_direction == "DOWN":
        recommendations.append("Điểm tuân thủ đang giảm, cần rà soát thay đổi gần đây trong checklist/minh chứng/CMDB.")
    if not recommendations:
        recommendations.append("Hồ sơ có trạng thái tuân thủ ổn định. Tiếp tục duy trì giám sát định kỳ.")

    return {
        "profile_id": profile.id,
        "profile_code": profile.profile_code,
        "proposed_level": profile.proposed_level,
        "management_score": management_score,
        "technical_score": technical_score,
        "evidence_score": evidence_score,
        "automation_score": automation_score,
        "overall_score": overall_score,
        "risk_level": risk_level,
        "trend_direction": trend_direction,
        "gap_count": gap_count,
        "mandatory_gap_count": mandatory_gap_count,
        "missing_evidence_count": missing_evidence_count,
        "open_finding_count": open_findings,
        "recommendations": recommendations,
    }


def create_monitoring_snapshot(db: Session, profile_id: int) -> tuple[ComplianceSnapshot, list[ComplianceMonitoringFinding], list[ComplianceMonitoringNotification]]:
    profile = db.get(LevelProfile, profile_id)
    if not profile:
        raise ValueError(f"Profile {profile_id} not found")
    score = calculate_profile_monitoring_score(db, profile_id)
    system_name, org_name = _system_org(db, profile)
    now = datetime.utcnow()
    snapshot = ComplianceSnapshot(
        snapshot_code=f"CMS-{now.strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:6].upper()}",
        profile_id=profile.id,
        profile_code=profile.profile_code,
        system_name=system_name,
        organization_name=org_name,
        proposed_level=profile.proposed_level,
        management_score=score["management_score"],
        technical_score=score["technical_score"],
        evidence_score=score["evidence_score"],
        automation_score=score["automation_score"],
        overall_score=score["overall_score"],
        risk_level=score["risk_level"],
        trend_direction=score["trend_direction"],
        gap_count=score["gap_count"],
        mandatory_gap_count=score["mandatory_gap_count"],
        missing_evidence_count=score["missing_evidence_count"],
        open_finding_count=score["open_finding_count"],
        snapshot_at=now,
        summary=f"Compliance score {score['overall_score']}%, risk {score['risk_level']}, trend {score['trend_direction']}.",
    )
    db.add(snapshot)
    db.flush()

    findings: list[ComplianceMonitoringFinding] = []
    def add_finding(kind: str, severity: str, title: str, description: str, recommendation: str):
        finding = ComplianceMonitoringFinding(
            snapshot_id=snapshot.id,
            profile_id=profile.id,
            finding_code=f"CMF-{uuid4().hex[:8].upper()}",
            finding_type=kind,
            severity=severity,
            title=title,
            description=description,
            recommendation=recommendation,
            status="OPEN",
        )
        db.add(finding)
        findings.append(finding)

    if score["mandatory_gap_count"] > 0:
        add_finding(
            "MANDATORY_GAP",
            "HIGH" if score["mandatory_gap_count"] < 5 else "CRITICAL",
            f"Hồ sơ {profile.profile_code} còn tiêu chí bắt buộc chưa đáp ứng",
            f"Số tiêu chí bắt buộc chưa đáp ứng: {score['mandatory_gap_count']}",
            "Hoàn thiện phương án khắc phục và bổ sung minh chứng trước khi gửi thẩm định.",
        )
    if score["missing_evidence_count"] > 0:
        add_finding(
            "EVIDENCE_GAP",
            "MEDIUM",
            f"Hồ sơ {profile.profile_code} thiếu minh chứng cho tiêu chí đã đáp ứng",
            f"Số tiêu chí đã đáp ứng nhưng chưa có minh chứng: {score['missing_evidence_count']}",
            "Bổ sung tài liệu minh chứng hoặc cập nhật lý do chưa có minh chứng.",
        )
    if score["trend_direction"] == "DOWN":
        add_finding(
            "SCORE_DECREASE",
            "HIGH",
            f"Điểm tuân thủ hồ sơ {profile.profile_code} đang giảm",
            "Điểm compliance mới thấp hơn snapshot trước ít nhất 5 điểm.",
            "Rà soát các thay đổi gần đây về checklist, rủi ro, CMDB và minh chứng.",
        )
    if score["overall_score"] < 70:
        add_finding(
            "LOW_SCORE",
            "HIGH" if score["overall_score"] >= 50 else "CRITICAL",
            f"Hồ sơ {profile.profile_code} có điểm tuân thủ thấp",
            f"Overall score hiện tại: {score['overall_score']}%.",
            "Ưu tiên xử lý gap bắt buộc, bổ sung minh chứng và đóng các finding đang mở.",
        )

    notifications: list[ComplianceMonitoringNotification] = []
    if score["risk_level"] in {"HIGH", "CRITICAL"} or score["trend_direction"] == "DOWN":
        notification = ComplianceMonitoringNotification(
            snapshot_id=snapshot.id,
            profile_id=profile.id,
            channel="IN_APP",
            event_type="COMPLIANCE_MONITORING_ALERT",
            recipient="SECURITY_OFFICER",
            subject=f"Cảnh báo compliance hồ sơ {profile.profile_code}",
            message=f"Hồ sơ {profile.profile_code} có score {score['overall_score']}%, risk {score['risk_level']}, trend {score['trend_direction']}.",
            status="DRY_RUN",
        )
        db.add(notification)
        notifications.append(notification)

    return snapshot, findings, notifications


def run_continuous_monitoring(db: Session, profile_id: int | None = None, scope: str = "ALL_PROFILES", create_notifications: bool = True) -> dict:
    stmt = select(LevelProfile)
    if profile_id:
        stmt = stmt.where(LevelProfile.id == profile_id)
    profiles = db.scalars(stmt.order_by(LevelProfile.id)).all()

    snapshots: list[ComplianceSnapshot] = []
    findings_count = 0
    notifications_count = 0
    for profile in profiles:
        snapshot, findings, notifications = create_monitoring_snapshot(db, profile.id)
        snapshots.append(snapshot)
        findings_count += len(findings)
        notifications_count += len(notifications) if create_notifications else 0
        if not create_notifications:
            for notification in notifications:
                db.delete(notification)

    db.commit()
    total = len(snapshots)
    avg = round(sum(s.overall_score for s in snapshots) / total) if total else 0
    recommendations = []
    if findings_count:
        recommendations.append("Có phát hiện compliance mới. Cần rà soát tab Findings và phân công người xử lý.")
    if avg < 75:
        recommendations.append("Điểm tuân thủ trung bình danh mục thấp. Cần ưu tiên các hồ sơ cấp độ 3 trở lên.")
    if not recommendations:
        recommendations.append("Danh mục hồ sơ đang ổn định. Tiếp tục duy trì giám sát hằng ngày.")
    return {
        "status": "COMPLETED",
        "scope": scope,
        "total_profiles": total,
        "snapshots_created": total,
        "findings_created": findings_count,
        "notifications_created": notifications_count if create_notifications else 0,
        "average_score": avg,
        "recommendations": recommendations,
    }


def latest_heatmap(db: Session) -> list[dict]:
    profiles = db.scalars(select(LevelProfile).order_by(LevelProfile.id)).all()
    items: list[dict] = []
    for profile in profiles:
        snap = _latest_snapshot(db, profile.id)
        if not snap:
            score = calculate_profile_monitoring_score(db, profile.id)
            system_name, org_name = _system_org(db, profile)
            overall = score["overall_score"]
            risk_level = score["risk_level"]
            item = {
                "profile_id": profile.id,
                "profile_code": profile.profile_code,
                "system_name": system_name,
                "organization_name": org_name,
                "proposed_level": profile.proposed_level,
                "overall_score": overall,
                "risk_level": risk_level,
                "heat_color": _heat_color(risk_level, overall),
                "mandatory_gap_count": score["mandatory_gap_count"],
                "missing_evidence_count": score["missing_evidence_count"],
                "open_finding_count": score["open_finding_count"],
            }
        else:
            item = {
                "profile_id": snap.profile_id,
                "profile_code": snap.profile_code,
                "system_name": snap.system_name,
                "organization_name": snap.organization_name,
                "proposed_level": snap.proposed_level,
                "overall_score": snap.overall_score,
                "risk_level": snap.risk_level,
                "heat_color": _heat_color(snap.risk_level, snap.overall_score),
                "mandatory_gap_count": snap.mandatory_gap_count,
                "missing_evidence_count": snap.missing_evidence_count,
                "open_finding_count": snap.open_finding_count,
            }
        items.append(item)
    return sorted(items, key=lambda x: (x["overall_score"], -x["proposed_level"]))


def monitoring_dashboard(db: Session) -> dict:
    snapshots = db.scalars(select(ComplianceSnapshot).order_by(ComplianceSnapshot.snapshot_at.desc(), ComplianceSnapshot.id.desc()).limit(10)).all()
    total_profiles = db.scalar(select(func.count(LevelProfile.id))) or 0
    avg = round(sum(s.overall_score for s in snapshots) / len(snapshots)) if snapshots else 0
    high_risk = db.scalar(select(func.count(ComplianceSnapshot.id)).where(ComplianceSnapshot.risk_level.in_(["HIGH", "CRITICAL"]))) or 0
    open_findings = db.scalar(select(func.count(ComplianceMonitoringFinding.id)).where(ComplianceMonitoringFinding.status == "OPEN")) or 0
    notifications = db.scalar(select(func.count(ComplianceMonitoringNotification.id))) or 0
    heat = latest_heatmap(db)
    recommendations = []
    if high_risk:
        recommendations.append("Ưu tiên xử lý các hồ sơ có màu đỏ/cam trên heatmap compliance.")
    if open_findings:
        recommendations.append("Theo dõi và đóng các finding compliance monitoring đang mở.")
    if not snapshots:
        recommendations.append("Chưa có snapshot. Hãy chạy Continuous Monitoring để khởi tạo baseline.")
    if not recommendations:
        recommendations.append("Danh mục hồ sơ đang được giám sát liên tục và chưa có cảnh báo nghiêm trọng.")
    return {
        "latest_snapshots": snapshots,
        "portfolio_average_score": avg,
        "total_profiles_monitored": total_profiles,
        "high_risk_profiles": high_risk,
        "open_findings": open_findings,
        "notifications": notifications,
        "top_risk_profiles": heat[:10],
        "recommendations": recommendations,
    }


def trend_for_profile(db: Session, profile_id: int, limit: int = 30) -> list[ComplianceSnapshot]:
    return db.scalars(
        select(ComplianceSnapshot)
        .where(ComplianceSnapshot.profile_id == profile_id)
        .order_by(ComplianceSnapshot.snapshot_at.desc(), ComplianceSnapshot.id.desc())
        .limit(limit)
    ).all()
