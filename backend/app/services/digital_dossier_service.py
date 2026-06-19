from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.evidence_document import EvidenceDocument
from app.models.level_profile import LevelProfile
from app.models.profile_requirement_answer import ProfileRequirementAnswer
from app.models.profile_signature import ProfileSignature
from app.models.profile_version import ProfileVersion
from app.models.security_requirement import SecurityRequirement
from app.models.user import User

STORAGE_ROOT = Path("/app/storage/signed-dossiers")


def _canonical_hash(data: dict[str, Any]) -> str:
    encoded = json.dumps(data, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_profile_snapshot(db: Session, profile_id: int) -> dict[str, Any]:
    profile = db.get(LevelProfile, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Level profile not found")

    answers = db.execute(
        select(ProfileRequirementAnswer, SecurityRequirement)
        .join(SecurityRequirement, SecurityRequirement.id == ProfileRequirementAnswer.requirement_id)
        .where(ProfileRequirementAnswer.profile_id == profile_id)
        .order_by(SecurityRequirement.code)
    ).all()
    evidence = db.scalars(select(EvidenceDocument).where(EvidenceDocument.profile_id == profile_id).order_by(EvidenceDocument.id)).all()

    return {
        "profile": {
            "id": profile.id,
            "profile_code": profile.profile_code,
            "information_system_id": profile.information_system_id,
            "proposed_level": profile.proposed_level,
            "status": profile.status,
            "basis_for_level": profile.basis_for_level,
            "system_scope_description": profile.system_scope_description,
            "technical_architecture": profile.technical_architecture,
            "confidentiality_impact": profile.confidentiality_impact,
            "integrity_impact": profile.integrity_impact,
            "availability_impact": profile.availability_impact,
        },
        "checklist": [
            {
                "requirement_code": req.code,
                "requirement_title": req.title,
                "category": req.category,
                "group_name": req.group_name,
                "status": ans.status,
                "current_state": ans.current_state,
                "improvement_plan": ans.improvement_plan,
                "owner": ans.owner,
                "due_date": str(ans.due_date) if ans.due_date else None,
                "evidence_count": ans.evidence_count,
            }
            for ans, req in answers
        ],
        "evidence": [
            {
                "id": doc.id,
                "document_type": doc.document_type,
                "original_filename": doc.original_filename,
                "version_no": doc.version,
                "file_size": doc.file_size,
                "checksum_sha256": doc.checksum_sha256,
            }
            for doc in evidence
        ],
    }


def create_profile_version(db: Session, profile_id: int, title: str | None, change_summary: str | None, user_id: int | None) -> ProfileVersion:
    profile = db.get(LevelProfile, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Level profile not found")
    snapshot = build_profile_snapshot(db, profile_id)
    snapshot_hash = _canonical_hash(snapshot)
    next_no = (db.scalar(select(func.max(ProfileVersion.version_no)).where(ProfileVersion.profile_id == profile_id)) or 0) + 1
    item = ProfileVersion(
        profile_id=profile_id,
        version_no=next_no,
        title=title or f"{profile.profile_code} - Phiên bản {next_no}",
        status="CREATED",
        snapshot_hash=snapshot_hash,
        snapshot_json=json.dumps(snapshot, ensure_ascii=False, sort_keys=True, default=str),
        change_summary=change_summary,
        created_by=user_id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_version_detail(item: ProfileVersion) -> dict[str, Any]:
    return {
        "id": item.id,
        "profile_id": item.profile_id,
        "version_no": item.version_no,
        "title": item.title,
        "status": item.status,
        "snapshot_hash": item.snapshot_hash,
        "change_summary": item.change_summary,
        "created_by": item.created_by,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
        "snapshot": json.loads(item.snapshot_json),
    }


def compare_versions(db: Session, from_version_id: int, to_version_id: int) -> dict[str, Any]:
    a = db.get(ProfileVersion, from_version_id)
    b = db.get(ProfileVersion, to_version_id)
    if not a or not b:
        raise HTTPException(status_code=404, detail="Version not found")
    if a.profile_id != b.profile_id:
        raise HTTPException(status_code=400, detail="Cannot compare versions from different profiles")
    sa = json.loads(a.snapshot_json)
    sb = json.loads(b.snapshot_json)
    changed_fields = [k for k in sorted(set(sa["profile"]) | set(sb["profile"])) if sa["profile"].get(k) != sb["profile"].get(k)]

    ca = {x["requirement_code"]: x for x in sa.get("checklist", [])}
    cb = {x["requirement_code"]: x for x in sb.get("checklist", [])}
    added_c = len(set(cb) - set(ca))
    removed_c = len(set(ca) - set(cb))
    changed_c = sum(1 for k in set(ca) & set(cb) if ca[k] != cb[k])

    ea = {x.get("checksum_sha256") or str(x.get("id")): x for x in sa.get("evidence", [])}
    eb = {x.get("checksum_sha256") or str(x.get("id")): x for x in sb.get("evidence", [])}
    added_e = len(set(eb) - set(ea))
    removed_e = len(set(ea) - set(eb))
    summary = []
    if changed_fields:
        summary.append(f"Thay đổi {len(changed_fields)} trường thuyết minh hồ sơ")
    if added_c or removed_c or changed_c:
        summary.append(f"Checklist: thêm {added_c}, xóa {removed_c}, thay đổi {changed_c}")
    if added_e or removed_e:
        summary.append(f"Minh chứng: thêm {added_e}, xóa {removed_e}")
    if not summary:
        summary.append("Không phát hiện khác biệt nghiệp vụ chính")
    return {
        "from_version": a.version_no,
        "to_version": b.version_no,
        "changed_fields": changed_fields,
        "added_checklist_items": added_c,
        "removed_checklist_items": removed_c,
        "changed_checklist_items": changed_c,
        "added_evidence_items": added_e,
        "removed_evidence_items": removed_e,
        "summary": summary,
    }


def sign_profile_version(db: Session, version_id: int, current_user: User, payload) -> ProfileSignature:
    version = db.get(ProfileVersion, version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    signer_name = payload.signer_name or current_user.full_name or current_user.username
    signer_role = payload.signer_role or "Internal signer"
    raw = f"{version.id}|{version.profile_id}|{version.snapshot_hash}|{current_user.id}|{signer_name}|{payload.comment or ''}"
    signature_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
    signed_path = STORAGE_ROOT / f"profile_{version.profile_id}_version_{version.version_no}_signature_{signature_hash[:12]}.txt"
    signed_path.write_text(
        "HỒ SƠ ĐIỆN TỬ ĐÃ KÝ SỐ MÔ PHỎNG\n"
        f"Profile ID: {version.profile_id}\nVersion: {version.version_no}\nSnapshot Hash: {version.snapshot_hash}\n"
        f"Signer: {signer_name}\nRole: {signer_role}\nSignature Hash: {signature_hash}\nComment: {payload.comment or ''}\n",
        encoding="utf-8",
    )
    item = ProfileSignature(
        profile_id=version.profile_id,
        version_id=version.id,
        signer_id=current_user.id,
        signer_name=signer_name,
        signer_role=signer_role,
        sign_method=payload.sign_method or "MOCK",
        status="SIGNED",
        signature_hash=signature_hash,
        certificate_subject=payload.certificate_subject or f"CN={signer_name}, O=LevelProfileManager Mock CA",
        signed_file_path=str(signed_path),
        comment=payload.comment,
    )
    version.status = "SIGNED"
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def dossier_summary(db: Session, profile_id: int) -> dict[str, Any]:
    latest = db.scalar(select(ProfileVersion).where(ProfileVersion.profile_id == profile_id).order_by(ProfileVersion.version_no.desc()).limit(1))
    total_versions = db.scalar(select(func.count(ProfileVersion.id)).where(ProfileVersion.profile_id == profile_id)) or 0
    total_signatures = db.scalar(select(func.count(ProfileSignature.id)).where(ProfileSignature.profile_id == profile_id)) or 0
    latest_sig = db.scalar(select(ProfileSignature).where(ProfileSignature.profile_id == profile_id).order_by(ProfileSignature.created_at.desc()).limit(1))
    return {
        "profile_id": profile_id,
        "total_versions": total_versions,
        "total_signatures": total_signatures,
        "latest_version_no": latest.version_no if latest else None,
        "latest_hash": latest.snapshot_hash if latest else None,
        "signed": bool(total_signatures),
        "latest_signature_status": latest_sig.status if latest_sig else None,
    }
