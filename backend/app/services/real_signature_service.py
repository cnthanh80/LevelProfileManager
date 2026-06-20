import hashlib
import json
import secrets
from datetime import datetime
from pathlib import Path
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.profile_signature import ProfileSignature
from app.models.profile_version import ProfileVersion
from app.models.signature_provider import SignatureProvider
from app.models.signature_request import SignatureRequest
from app.models.user import User
from app.schemas.real_signature import RealSignRequestCreate, SignatureCallbackPayload

SIGNED_DIR = Path("/app/storage/signed")
SIGNED_DIR.mkdir(parents=True, exist_ok=True)


def seed_default_signature_providers(db: Session) -> None:
    defaults = [
        ("MOCK-REMOTE", "Mock Remote Signing Gateway", "REMOTE_SIGNING", "ACTIVE", "https://signing-gateway.local/mock"),
        ("VNPT-CA", "VNPT CA Remote Signing", "REMOTE_SIGNING", "INACTIVE", "https://api.vnpt-ca.example/sign"),
        ("VIETTEL-CA", "Viettel CA Remote Signing", "REMOTE_SIGNING", "INACTIVE", "https://api.viettel-ca.example/sign"),
        ("HSM-INTERNAL", "Internal HSM Gateway", "HSM", "INACTIVE", "https://hsm-gateway.local/sign"),
    ]
    for code, name, provider_type, status, endpoint in defaults:
        obj = db.scalar(select(SignatureProvider).where(SignatureProvider.code == code))
        if not obj:
            db.add(SignatureProvider(
                code=code,
                name=name,
                provider_type=provider_type,
                status=status,
                endpoint_url=endpoint,
                callback_url="/api/v1/signature-requests/{request_code}/callback",
                description="Nhà cung cấp ký số mẫu. Khi triển khai thật cần thay endpoint, khóa API và luồng xác thực theo CA/HSM.",
                config_json=json.dumps({"mode": "placeholder", "requires_api_key": True}, ensure_ascii=False),
            ))
    db.commit()


def signature_gateway_status(db: Session) -> dict:
    providers_total = db.scalar(select(func.count(SignatureProvider.id))) or 0
    active_providers = db.scalar(select(func.count(SignatureProvider.id)).where(SignatureProvider.status == "ACTIVE")) or 0
    requests_total = db.scalar(select(func.count(SignatureRequest.id))) or 0
    pending_requests = db.scalar(select(func.count(SignatureRequest.id)).where(SignatureRequest.status.in_(["CREATED", "SENT", "PENDING"]))) or 0
    signed_requests = db.scalar(select(func.count(SignatureRequest.id)).where(SignatureRequest.status == "SIGNED")) or 0
    failed_requests = db.scalar(select(func.count(SignatureRequest.id)).where(SignatureRequest.status == "FAILED")) or 0
    return {
        "providers_total": providers_total,
        "active_providers": active_providers,
        "requests_total": requests_total,
        "pending_requests": pending_requests,
        "signed_requests": signed_requests,
        "failed_requests": failed_requests,
        "supported_methods": ["MOCK_REMOTE", "REMOTE_SIGNING", "USB_TOKEN", "HSM"],
        "production_note": "v3.2 cung cấp gateway tích hợp ký số thật theo adapter. Các CA/HSM cần cấu hình endpoint, xác thực API và mapping callback trước khi production.",
    }


def create_sign_request(db: Session, version_id: int, payload: RealSignRequestCreate, current_user: User) -> SignatureRequest:
    version = db.get(ProfileVersion, version_id)
    if not version:
        raise ValueError("Profile version not found")
    provider = db.get(SignatureProvider, payload.provider_id) if payload.provider_id else db.scalar(select(SignatureProvider).where(SignatureProvider.code == "MOCK-REMOTE"))
    if payload.provider_id and not provider:
        raise ValueError("Signature provider not found")
    request_code = "SIG-" + datetime.utcnow().strftime("%Y%m%d%H%M%S") + "-" + secrets.token_hex(4).upper()
    request_payload = {
        "version_id": version.id,
        "profile_id": version.profile_id,
        "document_hash": version.snapshot_hash,
        "signer_name": payload.signer_name or current_user.full_name or current_user.username,
        "signer_role": payload.signer_role or "Người ký hồ sơ",
        "callback_url": payload.callback_url or (provider.callback_url if provider else None),
        "note": payload.note,
    }
    item = SignatureRequest(
        profile_id=version.profile_id,
        version_id=version.id,
        provider_id=provider.id if provider else None,
        requested_by=current_user.id,
        request_code=request_code,
        sign_method=payload.sign_method,
        status="PENDING" if payload.sign_method != "MOCK_REMOTE" else "SENT",
        document_hash=version.snapshot_hash,
        request_payload_json=json.dumps(request_payload, ensure_ascii=False),
        provider_response_json=json.dumps({
            "provider": provider.code if provider else "MANUAL",
            "mode": "mock-gateway" if payload.sign_method == "MOCK_REMOTE" else "adapter-placeholder",
            "message": "Yêu cầu ký đã được tạo. Với CA/HSM thật, hệ thống ngoài sẽ callback trạng thái ký.",
        }, ensure_ascii=False),
        external_transaction_id="EXT-" + secrets.token_hex(8).upper(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def complete_sign_request(db: Session, request_code: str, payload: SignatureCallbackPayload) -> SignatureRequest:
    item = db.scalar(select(SignatureRequest).where(SignatureRequest.request_code == request_code))
    if not item:
        raise ValueError("Signature request not found")
    item.callback_payload_json = payload.model_dump_json()
    item.external_transaction_id = payload.external_transaction_id or item.external_transaction_id
    if payload.status == "SIGNED":
        signed_hash = payload.signed_hash or hashlib.sha256((item.document_hash + request_code + "SIGNED").encode("utf-8")).hexdigest()
        item.status = "SIGNED"
        item.signed_hash = signed_hash
        signed_path = SIGNED_DIR / f"{request_code}.txt"
        signed_path.write_text(
            f"DIGITAL SIGNATURE EVIDENCE\nRequest: {request_code}\nDocument hash: {item.document_hash}\nSigned hash: {signed_hash}\nSigned at: {datetime.utcnow().isoformat()}Z\n",
            encoding="utf-8",
        )
        item.signed_file_path = str(signed_path)
        signer_name = payload.signer_name or "Remote Signing Gateway"
        signer_role = payload.signer_role or "Remote signer"
        sig = ProfileSignature(
            profile_id=item.profile_id,
            version_id=item.version_id,
            signer_id=item.requested_by,
            signer_name=signer_name,
            signer_role=signer_role,
            sign_method="REMOTE_SIGNING",
            status="SIGNED",
            signature_hash=signed_hash,
            certificate_subject=payload.certificate_subject or "CN=Remote Signing Gateway,O=LevelProfileManager",
            signed_file_path=str(signed_path),
            comment=f"Ký số qua gateway: {request_code}",
        )
        db.add(sig)
        version = db.get(ProfileVersion, item.version_id)
        if version:
            version.status = "SIGNED"
    else:
        item.status = "FAILED"
        item.error_message = payload.error_message or "Signature callback returned failed status"
    db.commit()
    db.refresh(item)
    return item


def simulate_sign_request(db: Session, request_code: str) -> SignatureRequest:
    return complete_sign_request(db, request_code, SignatureCallbackPayload(status="SIGNED", signer_name="Mock Remote CA", signer_role="Remote Signing Gateway"))
