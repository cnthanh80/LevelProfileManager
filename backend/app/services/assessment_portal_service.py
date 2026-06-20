from datetime import datetime
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.assessment_portal import AssessmentCase, AssessmentFeedback


def normalize_case(case: AssessmentCase) -> None:
    if case.status:
        case.status = case.status.upper()
    if case.submission_method:
        case.submission_method = case.submission_method.upper()


def normalize_feedback(feedback: AssessmentFeedback) -> None:
    for attr in ["feedback_type", "severity", "status"]:
        value = getattr(feedback, attr, None)
        if isinstance(value, str):
            setattr(feedback, attr, value.upper())


def submit_case(db: Session, case: AssessmentCase) -> AssessmentCase:
    case.status = "SUBMITTED"
    case.submitted_at = datetime.utcnow()
    db.commit()
    db.refresh(case)
    return case


def complete_case(db: Session, case: AssessmentCase) -> AssessmentCase:
    case.status = "COMPLETED"
    case.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(case)
    return case


def get_assessment_summary(db: Session) -> dict:
    total_cases = db.scalar(select(func.count(AssessmentCase.id))) or 0
    draft_cases = db.scalar(select(func.count(AssessmentCase.id)).where(AssessmentCase.status == "DRAFT")) or 0
    submitted_cases = db.scalar(select(func.count(AssessmentCase.id)).where(AssessmentCase.status == "SUBMITTED")) or 0
    commented_cases = db.scalar(select(func.count(AssessmentCase.id)).where(AssessmentCase.status == "COMMENTED")) or 0
    completed_cases = db.scalar(select(func.count(AssessmentCase.id)).where(AssessmentCase.status == "COMPLETED")) or 0
    open_feedbacks = db.scalar(select(func.count(AssessmentFeedback.id)).where(AssessmentFeedback.status == "OPEN")) or 0
    critical_feedbacks = db.scalar(select(func.count(AssessmentFeedback.id)).where(AssessmentFeedback.severity == "CRITICAL", AssessmentFeedback.status != "CLOSED")) or 0
    return {
        "total_cases": total_cases,
        "draft_cases": draft_cases,
        "submitted_cases": submitted_cases,
        "commented_cases": commented_cases,
        "completed_cases": completed_cases,
        "open_feedbacks": open_feedbacks,
        "critical_feedbacks": critical_feedbacks,
    }
