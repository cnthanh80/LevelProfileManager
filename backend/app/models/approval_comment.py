from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class ApprovalComment(Base, TimestampMixin):
    __tablename__ = "approval_comments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("level_profiles.id"), nullable=False, index=True)
    workflow_state: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
