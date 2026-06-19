from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class ProfileAssessment(Base, TimestampMixin):
    __tablename__ = "profile_assessments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("level_profiles.id"), nullable=False, index=True)
    suggested_level: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    current_level: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    confidence_score: Mapped[int] = mapped_column(Integer, default=70, nullable=False)
    classification_reasons: Mapped[str | None] = mapped_column(Text)
    missing_requirements: Mapped[str | None] = mapped_column(Text)
    readiness_status: Mapped[str] = mapped_column(String(50), default="NOT_READY", nullable=False)
    readiness_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_ready_for_assessment: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    assessed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
