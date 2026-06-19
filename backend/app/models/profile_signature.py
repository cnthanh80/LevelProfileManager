from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin


class ProfileSignature(Base, TimestampMixin):
    __tablename__ = "profile_signatures"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("level_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    version_id: Mapped[int] = mapped_column(ForeignKey("profile_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    signer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    signer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    signer_role: Mapped[str | None] = mapped_column(String(100))
    sign_method: Mapped[str] = mapped_column(String(50), default="MOCK", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="SIGNED", nullable=False, index=True)
    signature_hash: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    certificate_subject: Mapped[str | None] = mapped_column(String(500))
    signed_file_path: Mapped[str | None] = mapped_column(String(1000))
    comment: Mapped[str | None] = mapped_column(Text)
