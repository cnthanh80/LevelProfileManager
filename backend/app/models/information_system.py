from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin


class InformationSystem(Base, TimestampMixin):
    __tablename__ = "information_systems"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_org_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"))
    operator_org_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"))
    manager_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    purpose: Mapped[str | None] = mapped_column(Text)
    scope: Mapped[str | None] = mapped_column(Text)
    main_functions: Mapped[str | None] = mapped_column(Text)
    user_groups: Mapped[str | None] = mapped_column(Text)
    data_types: Mapped[str | None] = mapped_column(Text)
    importance_level: Mapped[str | None] = mapped_column(String(100))
    deployment_model: Mapped[str | None] = mapped_column(String(50))
    environment: Mapped[str | None] = mapped_column(String(50))
    operation_status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    proposed_level: Mapped[int | None] = mapped_column(Integer)
