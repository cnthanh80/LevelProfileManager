from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import RequireReviewer, get_current_user, get_db
from app.models.user import User
from app.schemas.ai_classification import AiClassificationInput
from app.services.ai_classification_service import (
    classify_input,
    dashboard,
    list_profile_recommendations,
    misclassified_profiles,
    recommend_for_profile,
)

router = APIRouter()


@router.post("/ai/classify-level")
def ai_classify_level(payload: AiClassificationInput, current_user: User = RequireReviewer):
    return classify_input(payload)


@router.post("/profiles/{profile_id}/ai/recommend-level")
def ai_recommend_for_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = RequireReviewer,
):
    try:
        return recommend_for_profile(db, profile_id, actor_id=current_user.id, persist=True)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/profiles/{profile_id}/ai/recommendations")
def ai_recommendation_history(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_profile_recommendations(db, profile_id)


@router.get("/dashboard/ai-classification")
def ai_classification_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return dashboard(db)


@router.get("/dashboard/ai-classification/misclassified")
def ai_misclassified_profiles(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return misclassified_profiles(db)
