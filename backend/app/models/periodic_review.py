from datetime import date, datetime
from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class PeriodicReview(Base, TimestampMixin):
    __tablename__ = "periodic_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("level_profiles.id"), nullable=False, index=True)
    review_code: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    review_type: Mapped[str] = mapped_column(String(50), nullable=False, default="ANNUAL", index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PLANNED", index=True)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    assigned_to: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    completed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    findings: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
