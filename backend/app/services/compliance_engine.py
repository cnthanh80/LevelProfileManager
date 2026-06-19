import json
from collections import defaultdict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.compliance_score import ComplianceScore
from app.models.information_system import InformationSystem
from app.models.level_profile import LevelProfile
from app.models.profile_assessment import ProfileAssessment
from app.models.profile_requirement_answer import ProfileRequirementAnswer
from app.models.risk_assessment import RiskAssessment
from app.models.security_requirement import SecurityRequirement
from app.schemas.compliance import ClassificationInput


IMPACT_WEIGHT = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}


def _impact_value(value: str | None) -> int:
    return IMPACT_WEIGHT.get((value or "LOW").upper(), 1)


def classify_level(data: ClassificationInput) -> dict:
    level = 1
    reasons: list[str] = []

    if data.has_personal_data or data.user_count >= 500:
        level = max(level, 2)
        reasons.append("Có dữ liệu cá nhân hoặc quy mô người dùng từ 500 trở lên")
    if data.has_financial_data or data.internet_exposed or data.third_party_connections:
        level = max(level, 3)
        reasons.append("Có dữ liệu tài chính, công khai Internet hoặc kết nối bên thứ ba")
    if data.cross_org_connections or data.user_count >= 10000 or data.transaction_per_day >= 100000:
        level = max(level, 4)
        reasons.append("Hệ thống liên thông nhiều đơn vị hoặc có quy mô giao dịch/người dùng lớn")
    if data.has_state_secret_or_highly_sensitive_data:
        level = max(level, 5)
        reasons.append("Có dữ liệu đặc biệt quan trọng hoặc mức độ nhạy cảm rất cao")

    max_impact = max(
        _impact_value(data.downtime_impact),
        _impact_value(data.confidentiality_impact),
        _impact_value(data.integrity_impact),
        _impact_value(data.availability_impact),
    )
    if max_impact >= 3:
        level = max(level, 3)
        reasons.append("Tác động mất bí mật/toàn vẹn/sẵn sàng ở mức cao")
    if max_impact >= 4:
        level = max(level, 4)
        reasons.append("Tác động nghiệp vụ ở mức nghiêm trọng")

    confidence = min(95, 60 + len(reasons) * 10)
    if not reasons:
        reasons.append("Chưa có yếu tố rủi ro cao; tạm gợi ý cấp độ thấp")
    return {"suggested_level": level, "confidence_score": confidence, "reasons": reasons}


def suggest_level_from_profile(db: Session, profile: LevelProfile) -> dict:
    system = db.get(InformationSystem, profile.information_system_id)
    text = " ".join(
        [
            system.data_types or "" if system else "",
            system.importance_level or "" if system else "",
            system.deployment_model or "" if system else "",
            profile.confidentiality_impact or "",
            profile.integrity_impact or "",
            profile.availability_impact or "",
            profile.basis_for_level or "",
        ]
    ).lower()
    data = ClassificationInput(
        has_personal_data=any(x in text for x in ["cá nhân", "ca nhan", "personal"]),
        has_financial_data=any(x in text for x in ["tài chính", "tai chinh", "core", "ngân hàng", "ngan hang", "giao dịch", "giao dich"]),
        has_sensitive_data=any(x in text for x in ["nhạy cảm", "nhay cam", "sensitive"]),
        has_state_secret_or_highly_sensitive_data=any(x in text for x in ["bí mật", "bi mat", "tối mật", "toi mat"]),
        internet_exposed=any(x in text for x in ["internet", "public", "dmz"]),
        third_party_connections=any(x in text for x in ["api", "bên thứ ba", "ben thu ba", "third party"]),
        cross_org_connections=any(x in text for x in ["wan", "vpn", "liên thông", "lien thong"]),
        user_count=0,
        transaction_per_day=0,
        downtime_impact="HIGH" if any(x in text for x in ["cao", "high", "nghiêm trọng", "nghiem trong"]) else "MEDIUM",
        confidentiality_impact="HIGH" if any(x in text for x in ["bí mật", "bi mat", "nhạy cảm", "nhay cam"]) else "MEDIUM",
        integrity_impact="HIGH" if any(x in text for x in ["toàn vẹn", "toan ven", "sai lệch", "sai lech"]) else "MEDIUM",
        availability_impact="HIGH" if any(x in text for x in ["sẵn sàng", "san sang", "24/7", "gián đoạn", "gian doan"]) else "MEDIUM",
    )
    return classify_level(data)


def gap_analysis(db: Session, profile: LevelProfile) -> dict:
    requirements = db.scalars(
        select(SecurityRequirement)
        .where(SecurityRequirement.required_level <= profile.proposed_level)
        .order_by(SecurityRequirement.group_name, SecurityRequirement.sort_order, SecurityRequirement.code)
    ).all()
    answers = db.scalars(select(ProfileRequirementAnswer).where(ProfileRequirementAnswer.profile_id == profile.id)).all()
    answer_by_req = {a.requirement_id: a for a in answers}

    gaps = []
    compliant = non_compliant = not_applicable = missing = mandatory_gap = 0
    for req in requirements:
        ans = answer_by_req.get(req.id)
        status = ans.status if ans else None
        if status == "COMPLIANT":
            compliant += 1
        elif status == "NOT_APPLICABLE":
            not_applicable += 1
        elif status == "NON_COMPLIANT":
            non_compliant += 1
            gaps.append(req)
            if req.is_mandatory:
                mandatory_gap += 1
        else:
            missing += 1
            gaps.append(req)
            if req.is_mandatory:
                mandatory_gap += 1
    return {
        "profile_id": profile.id,
        "proposed_level": profile.proposed_level,
        "total_requirements": len(requirements),
        "compliant_count": compliant,
        "non_compliant_count": non_compliant,
        "not_applicable_count": not_applicable,
        "missing_answer_count": missing,
        "mandatory_gap_count": mandatory_gap,
        "gaps": [
            {
                "requirement_id": r.id,
                "code": r.code,
                "title": r.title,
                "group_name": r.group_name,
                "category": r.category,
                "is_mandatory": r.is_mandatory,
                "status": answer_by_req.get(r.id).status if answer_by_req.get(r.id) else None,
            }
            for r in gaps[:100]
        ],
    }


def calculate_compliance_score(db: Session, profile: LevelProfile) -> dict:
    requirements = db.scalars(select(SecurityRequirement).where(SecurityRequirement.required_level <= profile.proposed_level)).all()
    answers = db.scalars(select(ProfileRequirementAnswer).where(ProfileRequirementAnswer.profile_id == profile.id)).all()
    answer_by_req = {a.requirement_id: a for a in answers}

    group_totals = defaultdict(int)
    group_ok = defaultdict(int)
    mandatory_total = mandatory_ok = gap_total = 0
    for req in requirements:
        group_key = "management" if req.group_name.upper() in ["MANAGEMENT", "QUAN_LY", "QUẢN LÝ"] else "technical"
        group_totals[group_key] += 1
        ans = answer_by_req.get(req.id)
        ok = bool(ans and ans.status in ["COMPLIANT", "NOT_APPLICABLE"])
        if ok:
            group_ok[group_key] += 1
        else:
            gap_total += 1
        if req.is_mandatory:
            mandatory_total += 1
            if ans and ans.status == "COMPLIANT":
                mandatory_ok += 1

    def pct(ok: int, total: int) -> int:
        return int(round(ok * 100 / total)) if total else 0

    management = pct(group_ok["management"], group_totals["management"])
    technical = pct(group_ok["technical"], group_totals["technical"])
    overall = pct(group_ok["management"] + group_ok["technical"], group_totals["management"] + group_totals["technical"])
    return {
        "profile_id": profile.id,
        "management_score": management,
        "technical_score": technical,
        "overall_score": overall,
        "mandatory_total": mandatory_total,
        "mandatory_compliant": mandatory_ok,
        "gap_total": gap_total,
    }


def assess_risk(db: Session, profile: LevelProfile) -> dict:
    score = calculate_compliance_score(db, profile)
    gap = gap_analysis(db, profile)
    suggested = suggest_level_from_profile(db, profile)
    risk = 100 - score["overall_score"]
    factors = []
    if gap["mandatory_gap_count"] > 0:
        risk += min(25, gap["mandatory_gap_count"] * 3)
        factors.append(f"Còn {gap['mandatory_gap_count']} yêu cầu bắt buộc chưa đáp ứng")
    if suggested["suggested_level"] > profile.proposed_level:
        risk += 15
        factors.append(f"Engine gợi ý cấp độ {suggested['suggested_level']} cao hơn cấp độ đang khai báo {profile.proposed_level}")
    if profile.proposed_level >= 3 and score["technical_score"] < 70:
        risk += 10
        factors.append("Điểm đáp ứng kỹ thuật dưới 70% đối với hồ sơ cấp độ 3 trở lên")
    risk = max(0, min(100, risk))
    if risk >= 80:
        risk_level = "CRITICAL"
        recommendation = "Chưa nên gửi thẩm định; cần xử lý các yêu cầu bắt buộc và khoảng trống kỹ thuật trước."
    elif risk >= 60:
        risk_level = "HIGH"
        recommendation = "Cần lập kế hoạch bổ sung biện pháp và minh chứng trước khi trình phê duyệt."
    elif risk >= 35:
        risk_level = "MEDIUM"
        recommendation = "Có thể tiếp tục rà soát nội bộ, ưu tiên khắc phục các GAP còn lại."
    else:
        risk_level = "LOW"
        recommendation = "Hồ sơ có mức rủi ro thấp, có thể chuẩn bị trình rà soát/phê duyệt."
    if not factors:
        factors.append("Không phát hiện yếu tố rủi ro nổi bật từ dữ liệu hiện có")
    return {"profile_id": profile.id, "risk_score": risk, "risk_level": risk_level, "risk_factors": factors, "recommendation": recommendation}


def readiness(db: Session, profile: LevelProfile) -> dict:
    score = calculate_compliance_score(db, profile)
    gap = gap_analysis(db, profile)
    risk = assess_risk(db, profile)
    readiness_score = max(0, min(100, int(score["overall_score"] - gap["mandatory_gap_count"] * 2 - (10 if risk["risk_level"] in ["HIGH", "CRITICAL"] else 0))))
    blockers = []
    if gap["mandatory_gap_count"]:
        blockers.append(f"Còn {gap['mandatory_gap_count']} yêu cầu bắt buộc chưa đáp ứng")
    if score["overall_score"] < 75:
        blockers.append("Tỷ lệ đáp ứng tổng thể dưới 75%")
    if profile.proposed_level >= 3 and score["technical_score"] < 70:
        blockers.append("Tỷ lệ đáp ứng kỹ thuật dưới 70%")
    if risk["risk_level"] in ["HIGH", "CRITICAL"]:
        blockers.append(f"Mức rủi ro còn {risk['risk_level']}")
    ready = not blockers and readiness_score >= 75
    status = "READY_FOR_ASSESSMENT" if ready else "NOT_READY"
    return {"profile_id": profile.id, "readiness_score": readiness_score, "readiness_status": status, "is_ready_for_assessment": ready, "blockers": blockers}


def run_full_assessment(db: Session, profile: LevelProfile, assessed_by: int | None = None) -> dict:
    classification = suggest_level_from_profile(db, profile)
    gap = gap_analysis(db, profile)
    score = calculate_compliance_score(db, profile)
    risk = assess_risk(db, profile)
    rd = readiness(db, profile)

    pa = ProfileAssessment(
        profile_id=profile.id,
        suggested_level=classification["suggested_level"],
        current_level=profile.proposed_level,
        confidence_score=classification["confidence_score"],
        classification_reasons=json.dumps(classification["reasons"], ensure_ascii=False),
        missing_requirements=json.dumps(gap["gaps"][:50], ensure_ascii=False),
        readiness_status=rd["readiness_status"],
        readiness_score=rd["readiness_score"],
        is_ready_for_assessment=rd["is_ready_for_assessment"],
        assessed_by=assessed_by,
    )
    cs = ComplianceScore(profile_id=profile.id, **{k: v for k, v in score.items() if k != "profile_id"})
    ra = RiskAssessment(
        profile_id=profile.id,
        risk_score=risk["risk_score"],
        risk_level=risk["risk_level"],
        risk_factors=json.dumps(risk["risk_factors"], ensure_ascii=False),
        recommendation=risk["recommendation"],
    )
    db.add_all([pa, cs, ra])
    db.commit()
    db.refresh(pa)
    return {"assessment": pa, "classification": classification, "gap": gap, "score": score, "risk": risk, "readiness": rd}
