from sqlalchemy import ForeignKey, Integer, String, Text, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class EvidenceDocument(Base, TimestampMixin):
    __tablename__ = "evidence_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("level_profiles.id"), nullable=False, index=True)
    checklist_answer_id: Mapped[int | None] = mapped_column(ForeignKey("profile_requirement_answers.id"), nullable=True, index=True)
    document_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    uploaded_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
