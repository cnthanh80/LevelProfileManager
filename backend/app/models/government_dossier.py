from sqlalchemy import BigInteger, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class GovernmentDossier(Base, TimestampMixin):
    __tablename__ = "government_dossiers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("level_profiles.id"), nullable=False, index=True)
    dossier_code: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1, index=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="GENERATED", index=True)
    package_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    package_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    package_size: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    included_evidence_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    generated_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class GovernmentDossierFile(Base, TimestampMixin):
    __tablename__ = "government_dossier_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    dossier_id: Mapped[int] = mapped_column(ForeignKey("government_dossiers.id"), nullable=False, index=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("level_profiles.id"), nullable=False, index=True)
    file_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
