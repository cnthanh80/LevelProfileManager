from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field


class PeriodicReviewCreate(BaseModel):
    review_type: str = Field(default="ANNUAL", max_length=50)
    due_date: date
    assigned_to: int | None = None
    note: str | None = None


class GenerateNextReviewRequest(BaseModel):
    months: int = Field(default=12, ge=1, le=60)
    assigned_to: int | None = None
    note: str | None = "Tự động tạo lịch rà soát định kỳ tiếp theo"


class PeriodicReviewUpdate(BaseModel):
    status: str | None = None
    due_date: date | None = None
    assigned_to: int | None = None
    findings: str | None = None
    action_plan: str | None = None
    note: str | None = None


class PeriodicReviewComplete(BaseModel):
    findings: str = "Đã rà soát hồ sơ, chưa phát hiện điểm cần cập nhật lớn."
    action_plan: str | None = "Tiếp tục theo dõi và rà soát lại theo chu kỳ."


class PeriodicReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    profile_id: int
    review_code: str
    review_type: str
    status: str
    due_date: date
    assigned_to: int | None = None
    created_by: int | None = None
    completed_by: int | None = None
    completed_at: datetime | None = None
    findings: str | None = None
    action_plan: str | None = None
    note: str | None = None
    created_at: datetime
    updated_at: datetime


class ReviewSummary(BaseModel):
    total: int
    planned: int
    in_progress: int
    completed: int
    overdue: int
    due_soon: int
