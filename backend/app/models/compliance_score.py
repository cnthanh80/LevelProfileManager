from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class ComplianceScore(Base, TimestampMixin):
    __tablename__ = "compliance_scores"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("level_profiles.id"), nullable=False, index=True)
    management_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    technical_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    overall_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mandatory_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mandatory_compliant: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    gap_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    score_status: Mapped[str] = mapped_column(String(50), default="CALCULATED", nullable=False)
