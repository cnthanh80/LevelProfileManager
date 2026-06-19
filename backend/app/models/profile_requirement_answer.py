from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class ProfileRequirementAnswer(Base, TimestampMixin):
    __tablename__ = "profile_requirement_answers"
    __table_args__ = (
        UniqueConstraint("profile_id", "requirement_id", name="uq_profile_requirement_answer"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("level_profiles.id"), nullable=False, index=True)
    requirement_id: Mapped[int] = mapped_column(ForeignKey("security_requirements.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), default="NON_COMPLIANT", nullable=False, index=True)
    current_state: Mapped[str | None] = mapped_column(Text)
    improvement_plan: Mapped[str | None] = mapped_column(Text)
    evidence_note: Mapped[str | None] = mapped_column(Text)
    evidence_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    owner: Mapped[str | None] = mapped_column(String(255))
    due_date: Mapped[date | None] = mapped_column(Date)
