from __future__ import annotations

import json
from collections import Counter
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ai_level_recommendation import AiLevelRecommendation
from app.models.information_system import InformationSystem
from app.models.level_profile import LevelProfile
from app.models.profile_requirement_answer import ProfileRequirementAnswer
from app.models.security_requirement import SecurityRequirement
from app.schemas.ai_classification import AiClassificationInput

IMPACT_POINTS = {"LOW": 5, "MEDIUM": 15, "HIGH": 25, "CRITICAL": 35}



def _safe_text(value) -> str:
    """Convert nullable values to safe strings for NLP/rule-based classification."""
    if value is None:
        return ""
    return str(value).strip()


def _safe_join(values: list) -> str:
    """Join mixed/nullable values without raising TypeError."""
    return " ".join(_safe_text(v) for v in values if _safe_text(v))



def _contains(text: str, keywords: list[str]) -> bool:
    value = (text or "").lower()
    return any(k.lower() in value for k in keywords)


def _impact_points(value: str | None) -> int:
    return IMPACT_POINTS.get((value or "MEDIUM").upper(), 15)


def _risk_band(score: int) -> str:
    if score >= 85:
        return "CRITICAL"
    if score >= 65:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"


def _level_from_score(score: int) -> int:
    if score >= 90:
        return 5
    if score >= 70:
        return 4
    if score >= 45:
        return 3
    if score >= 25:
        return 2
    return 1


def _mismatch_status(current_level: int | None, recommended_level: int) -> str:
    if not current_level:
        return "NO_CURRENT_LEVEL"
    if current_level == recommended_level:
        return "MATCH"
    if current_level < recommended_level:
        return "UNDER_CLASSIFIED"
    return "OVER_CLASSIFIED"


def classify_input(payload: AiClassificationInput, current_level: int | None = None, profile_id: int | None = None, information_system_id: int | None = None) -> dict:
    reasons: list[str] = []
    evidence: list[str] = []
    actions: list[str] = []
    score = 0

    impact_score = max(
        _impact_points(payload.confidentiality_impact),
        _impact_points(payload.integrity_impact),
        _impact_points(payload.availability_impact),
        _impact_points(payload.business_criticality),
    )
    score += impact_score
    if impact_score >= 25:
        reasons.append("Tác động mất bí mật/toàn vẹn/sẵn sàng hoặc mức độ quan trọng nghiệp vụ ở mức cao.")
        evidence.append("CIA/business impact >= HIGH")

    if payload.has_personal_data:
        score += 12
        reasons.append("Hệ thống xử lý dữ liệu cá nhân hoặc dữ liệu người dùng.")
        evidence.append("personal_data=true")
    if payload.has_financial_data:
        score += 18
        reasons.append("Hệ thống xử lý dữ liệu tài chính/giao dịch nghiệp vụ quan trọng.")
        evidence.append("financial_data=true")
    if payload.has_sensitive_data:
        score += 12
        reasons.append("Có dữ liệu nhạy cảm hoặc dữ liệu nội bộ quan trọng.")
        evidence.append("sensitive_data=true")
    if payload.has_state_secret_or_highly_sensitive_data:
        score += 35
        reasons.append("Có dữ liệu bí mật nhà nước hoặc dữ liệu đặc biệt nhạy cảm.")
        evidence.append("state_secret_or_highly_sensitive=true")
    if payload.internet_exposed:
        score += 15
        reasons.append("Hệ thống có thành phần công khai Internet hoặc vùng DMZ.")
        evidence.append("internet_exposed=true")
    if payload.third_party_connections:
        score += 10
        reasons.append("Có kết nối API/bên thứ ba làm tăng bề mặt tấn công.")
        evidence.append("third_party_connections=true")
    if payload.cross_org_connections:
        score += 12
        reasons.append("Có liên thông WAN/VPN/liên tổ chức.")
        evidence.append("cross_org_connections=true")

    if payload.user_count >= 10000:
        score += 18
        reasons.append("Quy mô người dùng rất lớn.")
        evidence.append(f"user_count={payload.user_count}")
    elif payload.user_count >= 1000:
        score += 10
        reasons.append("Quy mô người dùng lớn.")
        evidence.append(f"user_count={payload.user_count}")
    elif payload.user_count >= 500:
        score += 6
        evidence.append(f"user_count={payload.user_count}")

    if payload.transaction_per_day >= 100000:
        score += 18
        reasons.append("Lưu lượng giao dịch/ngày rất lớn.")
        evidence.append(f"transaction_per_day={payload.transaction_per_day}")
    elif payload.transaction_per_day >= 10000:
        score += 10
        reasons.append("Lưu lượng giao dịch/ngày lớn.")
        evidence.append(f"transaction_per_day={payload.transaction_per_day}")

    text = " ".join([
        payload.system_name or "", payload.system_purpose or "", payload.data_description or "", payload.user_groups or "", payload.deployment_model or ""
    ]).lower()
    if _contains(text, ["core", "ngân hàng", "ngan hang", "thanh toán", "thanh toan", "giao dịch", "giao dich"]):
        score += 12
        reasons.append("Mô tả cho thấy hệ thống liên quan nghiệp vụ ngân hàng/giao dịch trọng yếu.")
        evidence.append("keyword=banking/core/transaction")
    if _contains(text, ["24/7", "không gián đoạn", "khong gian doan", "critical", "trọng yếu", "trong yeu"]):
        score += 10
        reasons.append("Hệ thống yêu cầu tính sẵn sàng cao/hoạt động liên tục.")
        evidence.append("keyword=24/7/critical")

    score = min(100, score)
    recommended_level = _level_from_score(score)
    if payload.has_state_secret_or_highly_sensitive_data:
        recommended_level = max(recommended_level, 5)
    if payload.has_financial_data or payload.internet_exposed or payload.third_party_connections:
        recommended_level = max(recommended_level, 3)
    if payload.cross_org_connections and (payload.user_count >= 10000 or payload.transaction_per_day >= 100000):
        recommended_level = max(recommended_level, 4)

    confidence = min(96, 55 + len(evidence) * 5 + (10 if impact_score >= 25 else 0))
    mismatch = _mismatch_status(current_level, recommended_level)
    if mismatch == "UNDER_CLASSIFIED":
        actions.append("Rà soát lại cấp độ đề xuất vì cấp độ hiện tại thấp hơn cấp độ engine khuyến nghị.")
    if recommended_level >= 3:
        actions.append("Bổ sung đầy đủ thuyết minh kiến trúc, kết nối, dữ liệu quan trọng và minh chứng kiểm soát kỹ thuật.")
    if recommended_level >= 4:
        actions.append("Tổ chức rà soát chuyên sâu về ảnh hưởng liên tổ chức, tính sẵn sàng, DR và giám sát ATTT.")
    if not actions:
        actions.append("Tiếp tục hoàn thiện checklist và minh chứng để tăng độ sẵn sàng thẩm định.")

    if not reasons:
        reasons.append("Chưa phát hiện yếu tố rủi ro nổi bật từ thông tin đầu vào; đề xuất cấp độ thấp và cần bổ sung dữ liệu đánh giá.")

    explanation = (
        f"Engine khuyến nghị cấp độ {recommended_level} với độ tin cậy {confidence}% "
        f"dựa trên điểm rủi ro {score}/100. "
        f"Trạng thái so với cấp độ hiện tại: {mismatch}."
    )
    return {
        "profile_id": profile_id,
        "information_system_id": information_system_id,
        "current_level": current_level,
        "recommended_level": recommended_level,
        "confidence_score": confidence,
        "risk_score": score,
        "risk_band": _risk_band(score),
        "mismatch_status": mismatch,
        "reasons": reasons,
        "evidence": evidence,
        "explanation": explanation,
        "recommended_actions": actions,
    }


def input_from_profile(db: Session, profile: LevelProfile) -> AiClassificationInput:
    system = db.get(InformationSystem, profile.information_system_id)

    text = _safe_join([
        system.name if system else None,
        system.purpose if system else None,
        system.scope if system else None,
        system.main_functions if system else None,
        system.user_groups if system else None,
        system.data_types if system else None,
        system.importance_level if system else None,
        system.deployment_model if system else None,
        profile.profile_code,
        profile.basis_for_level,
        profile.system_scope_description,
        profile.technical_architecture,
        profile.confidentiality_impact,
        profile.integrity_impact,
        profile.availability_impact,
    ])

    system_name = _safe_text(system.name if system else None) or _safe_text(profile.profile_code) or f"PROFILE-{profile.id}"
    system_purpose = _safe_text(system.purpose if system else None) or _safe_text(profile.system_scope_description)
    data_description = _safe_text(system.data_types if system else None) or _safe_text(profile.basis_for_level)
    user_groups = _safe_text(system.user_groups if system else None) or None
    deployment_model = _safe_text(system.deployment_model if system else None) or None
    importance_level = _safe_text(system.importance_level if system else None).upper()

    return AiClassificationInput(
        system_name=system_name,
        system_purpose=system_purpose,
        data_description=data_description,
        user_groups=user_groups,
        deployment_model=deployment_model,
        has_personal_data=_contains(text, ["cá nhân", "ca nhan", "personal", "khách hàng", "khach hang", "công dân", "cong dan"]),
        has_financial_data=_contains(text, ["tài chính", "tai chinh", "giao dịch", "giao dich", "ngân hàng", "ngan hang", "core", "kế toán", "ke toan"]),
        has_sensitive_data=_contains(text, ["nhạy cảm", "nhay cam", "sensitive", "mật", "mat", "nội bộ", "noi bo"]),
        has_state_secret_or_highly_sensitive_data=_contains(text, ["bí mật nhà nước", "bi mat nha nuoc", "tối mật", "toi mat", "tuyệt mật", "tuyet mat"]),
        internet_exposed=_contains(text, ["internet", "public", "dmz", "web", "mobile"]),
        third_party_connections=_contains(text, ["api", "bên thứ ba", "ben thu ba", "third party", "đối tác", "doi tac"]),
        cross_org_connections=_contains(text, ["wan", "vpn", "liên thông", "lien thong", "chi nhánh", "chi nhanh"]),
        user_count=0,
        transaction_per_day=0,
        confidentiality_impact=_map_impact(profile.confidentiality_impact),
        integrity_impact=_map_impact(profile.integrity_impact),
        availability_impact=_map_impact(profile.availability_impact),
        business_criticality="HIGH" if importance_level in {"HIGH", "CRITICAL", "CAO", "TRỌNG YẾU"} else "MEDIUM",
    )


def _map_impact(value: str | None) -> str:
    text = (value or "").lower()
    if _contains(text, ["critical", "nghiêm trọng", "nghiem trong", "rất cao", "rat cao"]):
        return "CRITICAL"
    if _contains(text, ["high", "cao", "lớn", "lon"]):
        return "HIGH"
    if _contains(text, ["low", "thấp", "thap"]):
        return "LOW"
    return "MEDIUM"


def recommend_for_profile(db: Session, profile_id: int, actor_id: int | None = None, persist: bool = True) -> dict:
    profile = db.get(LevelProfile, profile_id)
    if not profile:
        raise ValueError("Profile not found")
    payload = input_from_profile(db, profile)
    result = classify_input(payload, current_level=profile.proposed_level, profile_id=profile.id, information_system_id=profile.information_system_id)
    if persist:
        rec = AiLevelRecommendation(
            profile_id=profile.id,
            information_system_id=profile.information_system_id,
            current_level=profile.proposed_level,
            recommended_level=result["recommended_level"],
            confidence_score=result["confidence_score"],
            risk_score=result["risk_score"],
            risk_band=result["risk_band"],
            mismatch_status=result["mismatch_status"],
            input_summary=json.dumps(payload.model_dump(), ensure_ascii=False),
            reasons_json=json.dumps(result["reasons"], ensure_ascii=False),
            evidence_json=json.dumps(result["evidence"], ensure_ascii=False),
            explanation=result["explanation"],
            recommended_actions_json=json.dumps(result["recommended_actions"], ensure_ascii=False),
            created_by=actor_id,
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        result["recommendation_id"] = rec.id
    return result


def list_profile_recommendations(db: Session, profile_id: int) -> list[AiLevelRecommendation]:
    return db.scalars(
        select(AiLevelRecommendation)
        .where(AiLevelRecommendation.profile_id == profile_id)
        .order_by(AiLevelRecommendation.created_at.desc())
    ).all()


def dashboard(db: Session) -> dict:
    recs = db.scalars(select(AiLevelRecommendation).order_by(AiLevelRecommendation.created_at.desc())).all()
    profiles = db.scalars(select(LevelProfile)).all()
    if not recs:
        return {
            "recommendation_count": 0,
            "profile_count": len(profiles),
            "under_classified_count": 0,
            "risk_distribution": {},
            "level_distribution": {},
            "latest_recommendations": [],
        }
    risk_distribution = Counter(r.risk_band for r in recs)
    level_distribution = Counter(str(r.recommended_level) for r in recs)
    under = sum(1 for r in recs if r.mismatch_status == "UNDER_CLASSIFIED")
    latest = [
        {
            "id": r.id,
            "profile_id": r.profile_id,
            "current_level": r.current_level,
            "recommended_level": r.recommended_level,
            "confidence_score": r.confidence_score,
            "risk_score": r.risk_score,
            "risk_band": r.risk_band,
            "mismatch_status": r.mismatch_status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in recs[:10]
    ]
    return {
        "recommendation_count": len(recs),
        "profile_count": len(profiles),
        "under_classified_count": under,
        "risk_distribution": dict(risk_distribution),
        "level_distribution": dict(level_distribution),
        "latest_recommendations": latest,
    }


def misclassified_profiles(db: Session) -> list[dict]:
    recs = db.scalars(
        select(AiLevelRecommendation)
        .where(AiLevelRecommendation.mismatch_status == "UNDER_CLASSIFIED")
        .order_by(AiLevelRecommendation.risk_score.desc(), AiLevelRecommendation.created_at.desc())
    ).all()
    return [
        {
            "recommendation_id": r.id,
            "profile_id": r.profile_id,
            "current_level": r.current_level,
            "recommended_level": r.recommended_level,
            "risk_score": r.risk_score,
            "risk_band": r.risk_band,
            "confidence_score": r.confidence_score,
            "explanation": r.explanation,
        }
        for r in recs
    ]
