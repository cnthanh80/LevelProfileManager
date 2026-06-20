from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.assessment_portal import AssessmentCase
from app.models.assessment_workflow import AssessmentWorkflowEvent
from app.models.user import User
from app.schemas.assessment_workflow import AssessmentWorkflowEventRead, AssessmentWorkflowSummary, AssessmentWorkflowTransitionRequest, AssessmentWorkflowTransitionResult, AssessmentWorkflowRule
from app.services.assessment_workflow_service import get_workflow_summary, rule_list, transition_assessment_case

router = APIRouter()


@router.get('/assessment-workflow/rules', response_model=list[AssessmentWorkflowRule])
def get_rules(current_user: User = Depends(get_current_user)):
    return rule_list()


@router.get('/assessment-workflow/summary', response_model=AssessmentWorkflowSummary)
def summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_workflow_summary(db)


@router.get('/assessment-cases/{case_id}/workflow-events', response_model=list[AssessmentWorkflowEventRead])
def case_events(case_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    case = db.get(AssessmentCase, case_id)
    if not case:
        raise HTTPException(status_code=404, detail='Assessment case not found')
    return db.scalars(select(AssessmentWorkflowEvent).where(AssessmentWorkflowEvent.case_id == case_id).order_by(AssessmentWorkflowEvent.occurred_at.desc(), AssessmentWorkflowEvent.id.desc())).all()


@router.post('/assessment-cases/{case_id}/workflow-transition', response_model=AssessmentWorkflowTransitionResult)
def transition_case(case_id: int, payload: AssessmentWorkflowTransitionRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    case = db.get(AssessmentCase, case_id)
    if not case:
        raise HTTPException(status_code=404, detail='Assessment case not found')
    return transition_assessment_case(db, case, payload.action, current_user, payload.comment, payload.external_reference, payload.assessment_unit)
