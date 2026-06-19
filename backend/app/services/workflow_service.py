from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.level_profile import LevelProfile
from app.models.profile_requirement_answer import ProfileRequirementAnswer
from app.models.workflow_history import ProfileWorkflowHistory
from app.models.approval_comment import ApprovalComment
from app.models.role import Role
from app.models.user import User

WORKFLOW_STATES = [
    "DRAFT",
    "INTERNAL_REVIEW",
    "REVISION_REQUIRED",
    "REVIEWED",
    "LEADER_APPROVAL",
    "INTERNALLY_APPROVED",
    "SUBMITTED_FOR_ASSESSMENT",
    "ASSESSMENT_COMMENTED",
    "COMPLETED",
    "APPROVAL_DECISION_ISSUED",
    "REVIEW_DUE",
]

TRANSITIONS: dict[str, dict[str, str]] = {
    "DRAFT": {
        "submit_internal_review": "INTERNAL_REVIEW",
    },
    "REVISION_REQUIRED": {
        "resubmit_internal_review": "INTERNAL_REVIEW",
    },
    "INTERNAL_REVIEW": {
        "approve_review": "REVIEWED",
        "request_revision": "REVISION_REQUIRED",
    },
    "REVIEWED": {
        "submit_leader_approval": "LEADER_APPROVAL",
        "request_revision": "REVISION_REQUIRED",
    },
    "LEADER_APPROVAL": {
        "leader_approve": "INTERNALLY_APPROVED",
        "leader_request_revision": "REVISION_REQUIRED",
    },
    "INTERNALLY_APPROVED": {
        "submit_assessment": "SUBMITTED_FOR_ASSESSMENT",
    },
    "SUBMITTED_FOR_ASSESSMENT": {
        "receive_assessment_comment": "ASSESSMENT_COMMENTED",
        "mark_completed": "COMPLETED",
    },
    "ASSESSMENT_COMMENTED": {
        "complete_after_assessment": "COMPLETED",
        "request_revision": "REVISION_REQUIRED",
    },
    "COMPLETED": {
        "issue_approval_decision": "APPROVAL_DECISION_ISSUED",
    },
    "APPROVAL_DECISION_ISSUED": {
        "mark_review_due": "REVIEW_DUE",
    },
    "REVIEW_DUE": {
        "start_periodic_review": "DRAFT",
    },
}

ACTION_ROLE_RULES: dict[str, set[str]] = {
    "submit_internal_review": {"ADMIN", "SECURITY_OFFICER"},
    "resubmit_internal_review": {"ADMIN", "SECURITY_OFFICER"},
    "approve_review": {"ADMIN", "REVIEWER"},
    "request_revision": {"ADMIN", "REVIEWER", "SECURITY_OFFICER"},
    "submit_leader_approval": {"ADMIN", "REVIEWER", "SECURITY_OFFICER"},
    "leader_approve": {"ADMIN", "APPROVER"},
    "leader_request_revision": {"ADMIN", "APPROVER"},
    "submit_assessment": {"ADMIN", "SECURITY_OFFICER"},
    "receive_assessment_comment": {"ADMIN", "SECURITY_OFFICER", "REVIEWER"},
    "mark_completed": {"ADMIN", "SECURITY_OFFICER"},
    "complete_after_assessment": {"ADMIN", "SECURITY_OFFICER"},
    "issue_approval_decision": {"ADMIN", "SECURITY_OFFICER", "APPROVER"},
    "mark_review_due": {"ADMIN", "SECURITY_OFFICER"},
    "start_periodic_review": {"ADMIN", "SECURITY_OFFICER"},
}


def get_profile_or_404(db: Session, profile_id: int) -> LevelProfile:
    profile = db.get(LevelProfile, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Level profile not found")
    return profile


def get_user_role_code(db: Session, user: User) -> str | None:
    role = db.get(Role, user.role_id) if user.role_id else None
    return role.code if role else None


def allowed_actions_for_status(status_value: str) -> list[str]:
    return sorted(TRANSITIONS.get(status_value, {}).keys())


def ensure_user_can_do_action(db: Session, user: User, action: str) -> None:
    role_code = get_user_role_code(db, user)
    allowed_roles = ACTION_ROLE_RULES.get(action, set())
    if not role_code or role_code not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role {role_code or 'UNKNOWN'} is not allowed to perform action {action}",
        )


def validate_submit_requirements(db: Session, profile: LevelProfile, action: str) -> None:
    if action not in {"submit_internal_review", "resubmit_internal_review", "submit_leader_approval"}:
        return
    total_answers = db.scalar(
        select(ProfileRequirementAnswer.id)
        .where(ProfileRequirementAnswer.profile_id == profile.id)
        .limit(1)
    )
    if not total_answers:
        raise HTTPException(
            status_code=400,
            detail="Checklist has not been generated for this profile",
        )


def transition_profile(db: Session, profile: LevelProfile, action: str, comment: str | None, actor: User):
    current_status = profile.status
    next_status = TRANSITIONS.get(current_status, {}).get(action)
    if not next_status:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition: status={current_status}, action={action}",
        )

    ensure_user_can_do_action(db, actor, action)
    validate_submit_requirements(db, profile, action)

    profile.status = next_status
    history = ProfileWorkflowHistory(
        profile_id=profile.id,
        from_status=current_status,
        to_status=next_status,
        action=action,
        comment=comment,
        actor_user_id=actor.id,
    )
    db.add(history)

    if comment:
        db.add(ApprovalComment(
            profile_id=profile.id,
            workflow_state=next_status,
            action=action,
            comment=comment,
            created_by=actor.id,
        ))

    db.commit()
    db.refresh(profile)
    return current_status, next_status
