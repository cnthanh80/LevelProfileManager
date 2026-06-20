from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.compliance_automation import ComplianceAutomationFinding, ComplianceAutomationRule, ComplianceAutomationRun
from app.models.evidence_document import EvidenceDocument
from app.models.level_profile import LevelProfile
from app.models.periodic_review import PeriodicReview
from app.models.profile_requirement_answer import ProfileRequirementAnswer
from app.models.risk_register import RiskRegisterItem
from app.models.security_requirement import SecurityRequirement


def _norm(value: str | None, default: str = "MEDIUM") -> str:
    return (value or default).strip().upper()


def seed_default_automation_rules(db: Session) -> dict:
    defaults = [
        {
            "rule_code": "AUTO-MANDATORY-GAP",
            "rule_name": "Tiêu chí bắt buộc chưa đáp ứng",
            "rule_type": "MANDATORY_GAP",
            "severity": "HIGH",
            "threshold_value": 1,
            "description": "Phát hiện hồ sơ có tiêu chí bắt buộc đang Chưa đáp ứng.",
            "recommendation_template": "Yêu cầu đơn vị phụ trách bổ sung phương án khắc phục và minh chứng cho tiêu chí bắt buộc.",
        },
        {
            "rule_code": "AUTO-EVIDENCE-GAP",
            "rule_name": "Thiếu tài liệu minh chứng",
            "rule_type": "EVIDENCE_GAP",
            "severity": "MEDIUM",
            "threshold_value": 1,
            "description": "Phát hiện câu trả lời checklist chưa có minh chứng.",
            "recommendation_template": "Bổ sung file minh chứng hoặc ghi rõ lý do chưa có minh chứng.",
        },
        {
            "rule_code": "AUTO-HIGH-RISK-OPEN",
            "rule_name": "Rủi ro cao chưa xử lý",
            "rule_type": "HIGH_RISK_OPEN",
            "severity": "HIGH",
            "threshold_value": 15,
            "description": "Phát hiện rủi ro mở có điểm cao trong Risk Register.",
            "recommendation_template": "Phân công chủ trì xử lý rủi ro và cập nhật biện pháp giảm thiểu.",
        },
        {
            "rule_code": "AUTO-REVIEW-OVERDUE",
            "rule_name": "Hồ sơ quá hạn rà soát",
            "rule_type": "REVIEW_OVERDUE",
            "severity": "CRITICAL",
            "threshold_value": 0,
            "description": "Phát hiện đợt rà soát đã quá hạn nhưng chưa hoàn thành.",
            "recommendation_template": "Ưu tiên hoàn thành rà soát định kỳ và cập nhật kết quả vào hồ sơ.",
        },
    ]
    created = 0
    updated = 0
    for item in defaults:
        existing = db.scalar(select(ComplianceAutomationRule).where(ComplianceAutomationRule.rule_code == item["rule_code"]))
        if existing:
            for key, value in item.items():
                setattr(existing, key, value)
            updated += 1
        else:
            db.add(ComplianceAutomationRule(**item))
            created += 1
    db.commit()
    return {"status": "ok", "created": created, "updated": updated}


def _add_finding(findings, rule, profile_id, title, description):
    findings.append(
        ComplianceAutomationFinding(
            profile_id=profile_id,
            rule_code=rule.rule_code,
            finding_type=rule.rule_type,
            severity=_norm(rule.severity),
            title=title,
            description=description,
            recommendation=rule.recommendation_template,
            status="OPEN",
        )
    )


def run_compliance_automation(db: Session, profile_id: int | None = None, scope: str = "ALL_PROFILES", created_by: int | None = None) -> dict:
    seed_default_automation_rules(db)
    rules = db.scalars(select(ComplianceAutomationRule).where(ComplianceAutomationRule.is_enabled == True)).all()  # noqa: E712
    profiles_stmt = select(LevelProfile)
    if profile_id:
        profiles_stmt = profiles_stmt.where(LevelProfile.id == profile_id)
    profiles = db.scalars(profiles_stmt).all()

    run = ComplianceAutomationRun(
        run_code=f"AUTO-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:6].upper()}",
        scope=scope,
        profile_id=profile_id,
        status="RUNNING",
        total_profiles=len(profiles),
        started_at=datetime.utcnow(),
        created_by=created_by,
    )
    db.add(run)
    db.flush()

    findings = []
    rule_map = {r.rule_type: r for r in rules}

    for profile in profiles:
        mandatory_rule = rule_map.get("MANDATORY_GAP")
        if mandatory_rule:
            q = (
                select(ProfileRequirementAnswer)
                .join(SecurityRequirement, SecurityRequirement.id == ProfileRequirementAnswer.requirement_id)
                .where(
                    ProfileRequirementAnswer.profile_id == profile.id,
                    SecurityRequirement.is_mandatory == True,  # noqa: E712
                    ProfileRequirementAnswer.status == "NON_COMPLIANT",
                )
                .limit(10)
            )
            answers = db.scalars(q).all()
            for ans in answers:
                _add_finding(
                    findings,
                    mandatory_rule,
                    profile.id,
                    f"Hồ sơ {profile.profile_code} có tiêu chí bắt buộc chưa đáp ứng",
                    f"Checklist answer #{ans.id} đang ở trạng thái NON_COMPLIANT.",
                )

        evidence_rule = rule_map.get("EVIDENCE_GAP")
        if evidence_rule:
            missing = db.scalars(
                select(ProfileRequirementAnswer)
                .where(
                    ProfileRequirementAnswer.profile_id == profile.id,
                    ProfileRequirementAnswer.status == "COMPLIANT",
                    ProfileRequirementAnswer.evidence_count <= 0,
                )
                .limit(10)
            ).all()
            for ans in missing:
                _add_finding(
                    findings,
                    evidence_rule,
                    profile.id,
                    f"Hồ sơ {profile.profile_code} có tiêu chí đạt nhưng chưa có minh chứng",
                    f"Checklist answer #{ans.id} đang đánh dấu COMPLIANT nhưng evidence_count = {ans.evidence_count}.",
                )

        risk_rule = rule_map.get("HIGH_RISK_OPEN")
        if risk_rule:
            risks = db.scalars(
                select(RiskRegisterItem)
                .where(
                    RiskRegisterItem.profile_id == profile.id,
                    RiskRegisterItem.status != "CLOSED",
                    RiskRegisterItem.risk_score >= risk_rule.threshold_value,
                )
                .limit(10)
            ).all()
            for risk in risks:
                _add_finding(
                    findings,
                    risk_rule,
                    profile.id,
                    f"Rủi ro cao chưa xử lý: {risk.title}",
                    f"Risk {risk.risk_code} có điểm {risk.risk_score}, trạng thái {risk.status}.",
                )

        review_rule = rule_map.get("REVIEW_OVERDUE")
        if review_rule:
            reviews = db.scalars(
                select(PeriodicReview)
                .where(
                    PeriodicReview.profile_id == profile.id,
                    PeriodicReview.status != "COMPLETED",
                    PeriodicReview.due_date < date.today(),
                )
                .limit(10)
            ).all()
            for review in reviews:
                _add_finding(
                    findings,
                    review_rule,
                    profile.id,
                    f"Hồ sơ {profile.profile_code} quá hạn rà soát",
                    f"Đợt rà soát {review.review_code} hạn {review.due_date}, trạng thái {review.status}.",
                )

    for finding in findings:
        finding.run_id = run.id
        db.add(finding)

    critical = sum(1 for f in findings if f.severity == "CRITICAL")
    high = sum(1 for f in findings if f.severity == "HIGH")
    penalty = critical * 15 + high * 8 + (len(findings) - critical - high) * 3
    readiness = max(0, min(100, 100 - penalty))
    run.status = "COMPLETED"
    run.completed_at = datetime.utcnow()
    run.total_findings = len(findings)
    run.high_findings = high
    run.critical_findings = critical
    run.readiness_score = readiness
    run.executive_summary = f"Đã kiểm tra {len(profiles)} hồ sơ, phát hiện {len(findings)} vấn đề tuân thủ tự động. Readiness score: {readiness}%."
    db.commit()
    db.refresh(run)
    return {"run": run, "findings": findings}


def automation_dashboard(db: Session) -> dict:
    total_rules = db.scalar(select(func.count(ComplianceAutomationRule.id))) or 0
    enabled_rules = db.scalar(select(func.count(ComplianceAutomationRule.id)).where(ComplianceAutomationRule.is_enabled == True)) or 0  # noqa: E712
    total_runs = db.scalar(select(func.count(ComplianceAutomationRun.id))) or 0
    open_findings = db.scalar(select(func.count(ComplianceAutomationFinding.id)).where(ComplianceAutomationFinding.status == "OPEN")) or 0
    high_findings = db.scalar(select(func.count(ComplianceAutomationFinding.id)).where(ComplianceAutomationFinding.status == "OPEN", ComplianceAutomationFinding.severity == "HIGH")) or 0
    critical_findings = db.scalar(select(func.count(ComplianceAutomationFinding.id)).where(ComplianceAutomationFinding.status == "OPEN", ComplianceAutomationFinding.severity == "CRITICAL")) or 0
    last_run = db.scalars(select(ComplianceAutomationRun).order_by(ComplianceAutomationRun.id.desc()).limit(1)).first()
    recommendations = []
    if critical_findings:
        recommendations.append("Ưu tiên xử lý ngay các phát hiện CRITICAL trước khi gửi thẩm định hoặc phê duyệt.")
    if high_findings:
        recommendations.append("Yêu cầu đơn vị vận hành cập nhật phương án khắc phục cho các phát hiện HIGH.")
    if not recommendations:
        recommendations.append("Không có phát hiện nghiêm trọng đang mở. Tiếp tục duy trì rà soát định kỳ.")
    return {
        "total_rules": total_rules,
        "enabled_rules": enabled_rules,
        "total_runs": total_runs,
        "open_findings": open_findings,
        "high_findings": high_findings,
        "critical_findings": critical_findings,
        "last_run": last_run,
        "recommendations": recommendations,
    }
