from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin


class SignatureRequest(Base, TimestampMixin):
    __tablename__ = "signature_requests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("level_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    version_id: Mapped[int] = mapped_column(ForeignKey("profile_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_id: Mapped[int | None] = mapped_column(ForeignKey("signature_providers.id"))
    requested_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    request_code: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    sign_method: Mapped[str] = mapped_column(String(50), default="REMOTE_SIGNING", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="CREATED", nullable=False, index=True)
    document_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    request_payload_json: Mapped[str | None] = mapped_column(Text)
    provider_response_json: Mapped[str | None] = mapped_column(Text)
    callback_payload_json: Mapped[str | None] = mapped_column(Text)
    external_transaction_id: Mapped[str | None] = mapped_column(String(255))
    signed_hash: Mapped[str | None] = mapped_column(String(128))
    signed_file_path: Mapped[str | None] = mapped_column(String(1000))
    error_message: Mapped[str | None] = mapped_column(Text)
