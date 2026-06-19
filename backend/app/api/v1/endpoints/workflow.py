from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.approval_comment import ApprovalComment
from app.models.level_profile import LevelProfile
from app.models.workflow_history import ProfileWorkflowHistory
from app.models.user import User
from app.schemas.workflow import (
    ApprovalCommentCreate,
    ApprovalCommentRead,
    WorkflowHistoryRead,
    WorkflowState,
    WorkflowSummary,
    WorkflowSummaryItem,
    WorkflowTransitionRequest,
    WorkflowTransitionResponse,
)
from app.services.workflow_service import (
    allowed_actions_for_status,
    get_profile_or_404,
    transition_profile,
)

router = APIRouter()


@router.get("/profiles/{profile_id}/workflow", response_model=WorkflowState)
def get_profile_workflow(profile_id: int, db: Session = Depends(get_db)):
    profile = get_profile_or_404(db, profile_id)
    return WorkflowState(
        profile_id=profile.id,
        profile_code=profile.profile_code,
        current_status=profile.status,
        allowed_actions=allowed_actions_for_status(profile.status),
    )


@router.post("/profiles/{profile_id}/workflow/transition", response_model=WorkflowTransitionResponse)
def transition_profile_workflow(
    profile_id: int,
    payload: WorkflowTransitionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = get_profile_or_404(db, profile_id)
    from_status, to_status = transition_profile(
        db=db,
        profile=profile,
        action=payload.action,
        comment=payload.comment,
        actor=current_user,
    )
    return WorkflowTransitionResponse(
        profile_id=profile.id,
        from_status=from_status,
        to_status=to_status,
        action=payload.action,
        comment=payload.comment,
    )


@router.get("/profiles/{profile_id}/workflow/history", response_model=list[WorkflowHistoryRead])
def get_profile_workflow_history(
    profile_id: int,
    db: Session = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=500),
):
    get_profile_or_404(db, profile_id)
    return db.scalars(
        select(ProfileWorkflowHistory)
        .where(ProfileWorkflowHistory.profile_id == profile_id)
        .order_by(ProfileWorkflowHistory.id.desc())
        .limit(limit)
    ).all()


@router.post("/profiles/{profile_id}/comments", response_model=ApprovalCommentRead, status_code=status.HTTP_201_CREATED)
def create_approval_comment(
    profile_id: int,
    payload: ApprovalCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = get_profile_or_404(db, profile_id)
    comment = ApprovalComment(
        profile_id=profile.id,
        workflow_state=payload.workflow_state or profile.status,
        action=payload.action,
        comment=payload.comment,
        created_by=current_user.id,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("/profiles/{profile_id}/comments", response_model=list[ApprovalCommentRead])
def list_approval_comments(
    profile_id: int,
    db: Session = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=500),
):
    get_profile_or_404(db, profile_id)
    return db.scalars(
        select(ApprovalComment)
        .where(ApprovalComment.profile_id == profile_id)
        .order_by(ApprovalComment.id.desc())
        .limit(limit)
    ).all()


@router.get("/dashboard/workflow-summary", response_model=WorkflowSummary)
def get_workflow_summary(db: Session = Depends(get_db)):
    rows = db.execute(
        select(LevelProfile.status, func.count(LevelProfile.id))
        .group_by(LevelProfile.status)
        .order_by(LevelProfile.status)
    ).all()
    items = [WorkflowSummaryItem(status=row[0], total=row[1]) for row in rows]
    return WorkflowSummary(total=sum(item.total for item in items), items=items)
