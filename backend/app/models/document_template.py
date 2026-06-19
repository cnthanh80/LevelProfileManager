from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime

from app.models.base import Base, TimestampMixin


class DocumentTemplate(Base, TimestampMixin):
    __tablename__ = "document_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    document_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    category: Mapped[str] = mapped_column(String(100), nullable=False, default="GENERAL", index=True)
    official_number_prefix: Mapped[str | None] = mapped_column(String(100), nullable=True)
    variable_schema: Mapped[str | None] = mapped_column(Text, nullable=True)
    checksum_sha256: Mapped[str | None] = mapped_column(String(128), nullable=True)
    uploaded_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    uploaded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    agency_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_format: Mapped[str] = mapped_column(String(20), nullable=False, default="docx")
    template_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
