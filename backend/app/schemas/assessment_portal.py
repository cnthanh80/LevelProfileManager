from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class AssessmentCaseBase(BaseModel):
    case_code: str = Field(min_length=3, max_length=100)
    profile_id: int
    title: str = Field(min_length=3, max_length=255)
    assessment_unit: str | None = None
    contact_person: str | None = None
    contact_email: EmailStr | None = None
    submission_method: str = "PORTAL"
    status: str = "DRAFT"
    due_at: datetime | None = None
    summary: str | None = None


class AssessmentCaseCreate(AssessmentCaseBase):
    pass


class AssessmentCaseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    assessment_unit: str | None = None
    contact_person: str | None = None
    contact_email: EmailStr | None = None
    submission_method: str | None = None
    status: str | None = None
    due_at: datetime | None = None
    summary: str | None = None


class AssessmentCaseRead(AssessmentCaseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    submitted_at: datetime | None = None
    completed_at: datetime | None = None
    created_by: int | None = None
    created_at: datetime
    updated_at: datetime


class AssessmentFeedbackBase(BaseModel):
    case_id: int
    profile_id: int
    feedback_type: str = "COMMENT"
    severity: str = "MEDIUM"
    title: str = Field(min_length=3, max_length=255)
    content: str = Field(min_length=3)
    status: str = "OPEN"


class AssessmentFeedbackCreate(AssessmentFeedbackBase):
    pass


class AssessmentFeedbackUpdate(BaseModel):
    feedback_type: str | None = None
    severity: str | None = None
    title: str | None = None
    content: str | None = None
    status: str | None = None
    response: str | None = None


class AssessmentFeedbackRead(AssessmentFeedbackBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    response: str | None = None
    responded_by: int | None = None
    responded_at: datetime | None = None
    created_by: int | None = None
    created_at: datetime
    updated_at: datetime


class AssessmentFeedbackResponse(BaseModel):
    response: str = Field(min_length=3)
    status: str = "RESPONDED"


class AssessmentPortalSummary(BaseModel):
    total_cases: int
    draft_cases: int
    submitted_cases: int
    commented_cases: int
    completed_cases: int
    open_feedbacks: int
    critical_feedbacks: int
