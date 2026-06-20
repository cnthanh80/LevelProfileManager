from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class AssessmentCase(Base, TimestampMixin):
    __tablename__ = "assessment_cases"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    case_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("level_profiles.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    assessment_unit: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_person: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    submission_method: Mapped[str] = mapped_column(String(60), default="PORTAL", nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(60), default="DRAFT", nullable=False, index=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)


class AssessmentFeedback(Base, TimestampMixin):
    __tablename__ = "assessment_feedbacks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("assessment_cases.id"), nullable=False, index=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("level_profiles.id"), nullable=False, index=True)
    feedback_type: Mapped[str] = mapped_column(String(60), default="COMMENT", nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(30), default="MEDIUM", nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(60), default="OPEN", nullable=False, index=True)
    response: Mapped[str | None] = mapped_column(Text)
    responded_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
