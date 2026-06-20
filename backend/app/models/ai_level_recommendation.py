from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin


class AiLevelRecommendation(Base, TimestampMixin):
    __tablename__ = "ai_level_recommendations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("level_profiles.id"), nullable=False, index=True)
    information_system_id: Mapped[int | None] = mapped_column(ForeignKey("information_systems.id"), nullable=True, index=True)
    current_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    recommended_level: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    confidence_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    risk_band: Mapped[str] = mapped_column(String(30), nullable=False, default="LOW", index=True)
    mismatch_status: Mapped[str] = mapped_column(String(50), nullable=False, default="MATCH", index=True)
    input_summary: Mapped[str | None] = mapped_column(Text)
    reasons_json: Mapped[str | None] = mapped_column(Text)
    evidence_json: Mapped[str | None] = mapped_column(Text)
    explanation: Mapped[str | None] = mapped_column(Text)
    recommended_actions_json: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
