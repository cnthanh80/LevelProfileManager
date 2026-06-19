from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import RequireReviewer, get_current_user, get_db
from app.models.level_profile import LevelProfile
from app.models.profile_assessment import ProfileAssessment
from app.models.user import User
from app.schemas.compliance import ClassificationInput
from app.services.compliance_engine import (
    assess_risk,
    calculate_compliance_score,
    classify_level,
    gap_analysis,
    readiness,
    run_full_assessment,
    suggest_level_from_profile,
)

router = APIRouter()


def _get_profile_or_404(db: Session, profile_id: int) -> LevelProfile:
    profile = db.get(LevelProfile, profile_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


@router.post("/compliance/classify-level")
def classify_level_endpoint(payload: ClassificationInput, current_user: User = RequireReviewer):
    return classify_level(payload)


@router.get("/profiles/{profile_id}/compliance/suggest-level")
def suggest_level(profile_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = _get_profile_or_404(db, profile_id)
    return suggest_level_from_profile(db, profile)


@router.get("/profiles/{profile_id}/compliance/gap-analysis")
def get_gap_analysis(profile_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = _get_profile_or_404(db, profile_id)
    return gap_analysis(db, profile)


@router.get("/profiles/{profile_id}/compliance/score")
def get_compliance_score(profile_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = _get_profile_or_404(db, profile_id)
    return calculate_compliance_score(db, profile)


@router.get("/profiles/{profile_id}/compliance/risk")
def get_risk(profile_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = _get_profile_or_404(db, profile_id)
    return assess_risk(db, profile)


@router.get("/profiles/{profile_id}/compliance/readiness")
def get_readiness(profile_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = _get_profile_or_404(db, profile_id)
    return readiness(db, profile)


@router.post("/profiles/{profile_id}/compliance/run-assessment")
def run_assessment(profile_id: int, db: Session = Depends(get_db), current_user: User = RequireReviewer):
    profile = _get_profile_or_404(db, profile_id)
    return run_full_assessment(db, profile, assessed_by=current_user.id)


@router.get("/profiles/{profile_id}/compliance/assessments")
def list_assessments(profile_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _get_profile_or_404(db, profile_id)
    return db.scalars(
        select(ProfileAssessment)
        .where(ProfileAssessment.profile_id == profile_id)
        .order_by(ProfileAssessment.created_at.desc())
    ).all()


@router.get("/dashboard/compliance")
def dashboard_compliance(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profiles = db.scalars(select(LevelProfile)).all()
    if not profiles:
        return {"profile_count": 0, "overall": 0, "management": 0, "technical": 0, "risk": "LOW", "ready_count": 0}

    total_overall = total_mgmt = total_tech = 0
    risk_levels = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    ready_count = 0
    for profile in profiles:
        score = calculate_compliance_score(db, profile)
        total_overall += score["overall_score"]
        total_mgmt += score["management_score"]
        total_tech += score["technical_score"]
        risk = assess_risk(db, profile)
        risk_levels[risk["risk_level"]] = risk_levels.get(risk["risk_level"], 0) + 1
        rd = readiness(db, profile)
        if rd["is_ready_for_assessment"]:
            ready_count += 1
    count = len(profiles)
    dominant_risk = max(risk_levels.items(), key=lambda x: x[1])[0]
    return {
        "profile_count": count,
        "overall": int(round(total_overall / count)),
        "management": int(round(total_mgmt / count)),
        "technical": int(round(total_tech / count)),
        "risk": dominant_risk,
        "risk_distribution": risk_levels,
        "ready_count": ready_count,
        "not_ready_count": count - ready_count,
    }
