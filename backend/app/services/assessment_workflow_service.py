from __future__ import annotations

from datetime import datetime
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.assessment_portal import AssessmentCase
from app.models.assessment_workflow import AssessmentWorkflowEvent
from app.models.user import User

RULES: dict[tuple[str, str], tuple[str, list[str], str]] = {
    ("DRAFT", "submit_to_security_review"): ("SECURITY_REVIEW", ["ADMIN", "SECURITY_OFFICER"], "Gửi hồ sơ sang cán bộ ATTT rà soát"),
    ("SECURITY_REVIEW", "request_internal_revision"): ("INTERNAL_REVISION_REQUIRED", ["ADMIN", "SECURITY_OFFICER", "REVIEWER"], "Yêu cầu đơn vị vận hành chỉnh sửa nội bộ"),
    ("INTERNAL_REVISION_REQUIRED", "resubmit_to_security_review"): ("SECURITY_REVIEW", ["ADMIN", "SECURITY_OFFICER"], "Gửi lại sau khi chỉnh sửa"),
    ("SECURITY_REVIEW", "approve_for_external_assessment"): ("READY_FOR_EXTERNAL_ASSESSMENT", ["ADMIN", "REVIEWER", "APPROVER"], "Đủ điều kiện gửi thẩm định"),
    ("READY_FOR_EXTERNAL_ASSESSMENT", "send_external_assessment"): ("SENT_TO_ASSESSMENT_UNIT", ["ADMIN", "SECURITY_OFFICER", "APPROVER"], "Đã gửi đơn vị thẩm định"),
    ("SENT_TO_ASSESSMENT_UNIT", "receive_assessment_comments"): ("ASSESSMENT_COMMENTS_RECEIVED", ["ADMIN", "SECURITY_OFFICER", "REVIEWER"], "Nhận ý kiến thẩm định"),
    ("ASSESSMENT_COMMENTS_RECEIVED", "request_clarification"): ("CLARIFICATION_REQUIRED", ["ADMIN", "SECURITY_OFFICER", "REVIEWER"], "Yêu cầu giải trình/bổ sung"),
    ("CLARIFICATION_REQUIRED", "submit_clarification"): ("CLARIFICATION_SUBMITTED", ["ADMIN", "SECURITY_OFFICER"], "Đã gửi giải trình/bổ sung"),
    ("CLARIFICATION_SUBMITTED", "receive_assessment_comments"): ("ASSESSMENT_COMMENTS_RECEIVED", ["ADMIN", "SECURITY_OFFICER", "REVIEWER"], "Nhận ý kiến thẩm định tiếp theo"),
    ("ASSESSMENT_COMMENTS_RECEIVED", "approve_assessment_result"): ("ASSESSMENT_APPROVED", ["ADMIN", "APPROVER"], "Kết quả thẩm định đạt yêu cầu"),
    ("ASSESSMENT_COMMENTS_RECEIVED", "reject_assessment_result"): ("ASSESSMENT_REJECTED", ["ADMIN", "APPROVER"], "Kết quả thẩm định chưa đạt"),
    ("ASSESSMENT_APPROVED", "issue_approval_decision"): ("APPROVAL_DECISION_ISSUED", ["ADMIN", "APPROVER"], "Đã ban hành quyết định phê duyệt"),
}

DISPLAY = {
    "DRAFT": "Nháp",
    "SECURITY_REVIEW": "ATTT rà soát",
    "INTERNAL_REVISION_REQUIRED": "Yêu cầu chỉnh sửa nội bộ",
    "READY_FOR_EXTERNAL_ASSESSMENT": "Sẵn sàng gửi thẩm định",
    "SENT_TO_ASSESSMENT_UNIT": "Đã gửi thẩm định",
    "ASSESSMENT_COMMENTS_RECEIVED": "Có ý kiến thẩm định",
    "CLARIFICATION_REQUIRED": "Yêu cầu giải trình/bổ sung",
    "CLARIFICATION_SUBMITTED": "Đã gửi giải trình",
    "ASSESSMENT_APPROVED": "Thẩm định đạt",
    "ASSESSMENT_REJECTED": "Thẩm định không đạt",
    "APPROVAL_DECISION_ISSUED": "Đã có quyết định phê duyệt",
}


def user_role_names(user: User) -> list[str]:
    names = []
    role = getattr(user, "role", None)
    if role and getattr(role, "name", None):
        names.append(str(role.name).upper())
    role_name = getattr(user, "role_name", None)
    if role_name:
        names.append(str(role_name).upper())
    if not names:
        names.append("USER")
    return list(dict.fromkeys(names))


def rule_list():
    return [
        {"from_status": k[0], "action": k[1], "to_status": v[0], "allowed_roles": v[1], "description": v[2]}
        for k, v in RULES.items()
    ]


def transition_assessment_case(db: Session, case: AssessmentCase, action: str, user: User, comment: str | None = None, external_reference: str | None = None, assessment_unit: str | None = None):
    current = (case.status or "DRAFT").upper()
    normalized_action = action.lower().strip()
    rule = RULES.get((current, normalized_action))
    if not rule:
        valid = [a for (from_status, a) in RULES.keys() if from_status == current]
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": "Invalid assessment workflow transition", "current_status": current, "action": normalized_action, "valid_actions": valid})

    to_status, allowed_roles, description = rule
    roles = user_role_names(user)
    if "ADMIN" not in roles and not set(roles).intersection(set(allowed_roles)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"message": "User role is not allowed for this assessment transition", "allowed_roles": allowed_roles, "user_roles": roles})

    previous = case.status
    case.status = to_status
    if normalized_action == "send_external_assessment":
        case.submitted_at = case.submitted_at or datetime.utcnow()
        if assessment_unit:
            case.assessment_unit = assessment_unit
    if normalized_action == "issue_approval_decision":
        case.completed_at = datetime.utcnow()
    if assessment_unit:
        case.assessment_unit = assessment_unit

    event = AssessmentWorkflowEvent(
        case_id=case.id,
        profile_id=case.profile_id,
        from_status=previous,
        to_status=to_status,
        action=normalized_action,
        actor_role=",".join(roles),
        comment=comment or description,
        external_reference=external_reference,
        assessment_unit=assessment_unit or case.assessment_unit,
        created_by=getattr(user, "id", None),
        occurred_at=datetime.utcnow(),
    )
    db.add(event)
    db.commit()
    db.refresh(case)
    db.refresh(event)
    return {"case_id": case.id, "profile_id": case.profile_id, "previous_status": previous, "current_status": case.status, "action": normalized_action, "message": description, "event": event}


def get_workflow_summary(db: Session):
    rows = db.execute(select(AssessmentCase.status, func.count(AssessmentCase.id)).group_by(AssessmentCase.status)).all()
    by_status = {str(status or "UNKNOWN"): int(count) for status, count in rows}
    now = datetime.utcnow()
    overdue = db.scalar(select(func.count(AssessmentCase.id)).where(AssessmentCase.due_at.is_not(None), AssessmentCase.due_at < now, AssessmentCase.status.notin_(["APPROVAL_DECISION_ISSUED", "ASSESSMENT_REJECTED"]))) or 0
    return {
        "total_cases": sum(by_status.values()),
        "by_status": by_status,
        "pending_external_assessment": by_status.get("READY_FOR_EXTERNAL_ASSESSMENT", 0) + by_status.get("SENT_TO_ASSESSMENT_UNIT", 0),
        "waiting_for_clarification": by_status.get("CLARIFICATION_REQUIRED", 0),
        "approved_cases": by_status.get("ASSESSMENT_APPROVED", 0) + by_status.get("APPROVAL_DECISION_ISSUED", 0),
        "rejected_cases": by_status.get("ASSESSMENT_REJECTED", 0),
        "overdue_cases": int(overdue),
        "rules": rule_list(),
    }
