from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin


class LevelProfile(Base, TimestampMixin):
    __tablename__ = "level_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    profile_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    information_system_id: Mapped[int] = mapped_column(ForeignKey("information_systems.id"), nullable=False)
    proposed_level: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(80), default="DRAFT", nullable=False, index=True)
    basis_for_level: Mapped[str | None] = mapped_column(Text)
    system_scope_description: Mapped[str | None] = mapped_column(Text)
    technical_architecture: Mapped[str | None] = mapped_column(Text)
    confidentiality_impact: Mapped[str | None] = mapped_column(Text)
    integrity_impact: Mapped[str | None] = mapped_column(Text)
    availability_impact: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    locked_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
