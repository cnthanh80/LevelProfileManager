from collections import Counter
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.security_event import SecurityEvent
from app.models.siem_integration import SiemConnector, SiemCorrelationRule, SiemEvent

SEVERITY_SCORE = {"INFO": 5, "LOW": 15, "MEDIUM": 35, "HIGH": 70, "CRITICAL": 95}


def norm(value: str | None, default: str) -> str:
    return (value or default).strip().upper()


def siem_status(db: Session) -> dict:
    enabled = db.scalar(select(func.count(SiemConnector.id)).where(SiemConnector.is_enabled == True)) or 0  # noqa: E712
    return {
        "status": "READY",
        "version": "3.6.0",
        "supported_integrations": ["SYSLOG", "CEF", "LEEF", "WEBHOOK", "SPLUNK", "QRADAR", "ELASTIC", "MICROSOFT_SENTINEL", "MOCK"],
        "enabled_connectors": enabled,
        "message": "SIEM & Audit Integration foundation is ready. Production connectors require secure network/API configuration.",
    }


def seed_default_connectors(db: Session) -> dict:
    defaults = [
        {"connector_code": "MOCK-SIEM", "connector_name": "Mock SIEM Gateway", "connector_type": "MOCK", "endpoint_url": "http://mock-siem.local/events", "auth_type": "NONE", "description": "Dùng để kiểm thử tích hợp SIEM nội bộ."},
        {"connector_code": "SYSLOG-CEF", "connector_name": "Syslog CEF Collector", "connector_type": "CEF", "endpoint_url": "udp://siem.local:514", "auth_type": "NONE", "description": "Kênh đẩy sự kiện CEF/Syslog."},
        {"connector_code": "WEBHOOK-SIEM", "connector_name": "Webhook SIEM API", "connector_type": "WEBHOOK", "endpoint_url": "https://siem.example.org/api/events", "auth_type": "TOKEN", "description": "Kênh webhook cho SIEM/SOC."},
    ]
    created = 0
    updated = 0
    for item in defaults:
        existing = db.scalar(select(SiemConnector).where(SiemConnector.connector_code == item["connector_code"]))
        if existing:
            for k, v in item.items():
                setattr(existing, k, v)
            updated += 1
        else:
            db.add(SiemConnector(**item))
            created += 1
    db.commit()
    return {"status": "ok", "created": created, "updated": updated}


def seed_default_rules(db: Session) -> dict:
    defaults = [
        {"rule_code": "AUTH-FAIL-BRUTE", "rule_name": "Nhiều lần đăng nhập thất bại", "event_type": "AUTH_FAILURE", "min_severity": "MEDIUM", "threshold_count": 5, "window_minutes": 15, "risk_score": 75, "action_hint": "Kiểm tra tài khoản/IP nguồn và xem xét khóa tạm thời."},
        {"rule_code": "PROFILE-CRITICAL-CHANGE", "rule_name": "Thay đổi hồ sơ cấp độ quan trọng", "event_type": "PROFILE_CHANGE", "min_severity": "HIGH", "threshold_count": 1, "window_minutes": 60, "risk_score": 70, "action_hint": "Rà soát audit trail và xác nhận phê duyệt thay đổi."},
        {"rule_code": "SIGNATURE-FAIL", "rule_name": "Lỗi ký số/hồ sơ điện tử", "event_type": "SIGNATURE_FAILURE", "min_severity": "HIGH", "threshold_count": 1, "window_minutes": 30, "risk_score": 80, "action_hint": "Kiểm tra gateway ký số, chứng thư và trạng thái yêu cầu ký."},
        {"rule_code": "SECURITY-CRITICAL", "rule_name": "Sự kiện bảo mật nghiêm trọng", "event_type": None, "min_severity": "CRITICAL", "threshold_count": 1, "window_minutes": 10, "risk_score": 90, "action_hint": "Kích hoạt quy trình ứng cứu sự cố ATTT."},
    ]
    created = 0
    updated = 0
    for item in defaults:
        existing = db.scalar(select(SiemCorrelationRule).where(SiemCorrelationRule.rule_code == item["rule_code"]))
        if existing:
            for k, v in item.items():
                setattr(existing, k, v)
            updated += 1
        else:
            db.add(SiemCorrelationRule(**item))
            created += 1
    db.commit()
    return {"status": "ok", "created": created, "updated": updated}


def ingest_event(db: Session, payload: dict) -> SiemEvent:
    data = dict(payload)
    data["event_type"] = norm(data.get("event_type"), "GENERIC")
    data["severity"] = norm(data.get("severity"), "INFO")
    data["status"] = norm(data.get("status"), "OPEN")
    if not data.get("correlation_key"):
        data["correlation_key"] = ":".join(filter(None, [data.get("event_type"), data.get("username"), data.get("ip_address"), data.get("asset_code")]))[:200] or data["event_type"]
    if not data.get("normalized_message"):
        data["normalized_message"] = data.get("raw_message") or f"{data['event_type']} - {data['severity']}"
    event = SiemEvent(**data)
    db.add(event)
    connector_id = data.get("connector_id")
    if connector_id:
        connector = db.get(SiemConnector, connector_id)
        if connector:
            connector.last_sync_at = datetime.utcnow()
    db.commit()
    db.refresh(event)
    return event


def ingest_from_audit(db: Session, limit: int = 20) -> dict:
    connector = db.scalar(select(SiemConnector).where(SiemConnector.connector_code == "MOCK-SIEM"))
    connector_id = connector.id if connector else None
    logs = db.scalars(select(AuditLog).order_by(AuditLog.id.desc()).limit(limit)).all()
    created = 0
    for log in logs:
        key = f"AUDIT:{log.id}"
        if db.scalar(select(SiemEvent).where(SiemEvent.correlation_key == key)):
            continue
        severity = "HIGH" if (log.status_code or 200) >= 500 else "INFO"
        event_type = "API_ERROR" if severity == "HIGH" else "AUDIT_EVENT"
        db.add(SiemEvent(
            connector_id=connector_id,
            source_system="LevelProfileManager",
            event_type=event_type,
            severity=severity,
            status="OPEN" if severity == "HIGH" else "CLOSED",
            ip_address=log.ip_address,
            correlation_key=key,
            raw_message=log.detail,
            normalized_message=f"{log.http_method or ''} {log.path or ''} => {log.status_code or ''}",
        ))
        created += 1
    db.commit()
    return {"status": "ok", "created": created, "source": "audit_logs"}


def ingest_from_security_events(db: Session, limit: int = 20) -> dict:
    connector = db.scalar(select(SiemConnector).where(SiemConnector.connector_code == "MOCK-SIEM"))
    connector_id = connector.id if connector else None
    events = db.scalars(select(SecurityEvent).order_by(SecurityEvent.id.desc()).limit(limit)).all()
    created = 0
    for sec in events:
        key = f"SECURITY:{sec.id}"
        if db.scalar(select(SiemEvent).where(SiemEvent.correlation_key == key)):
            continue
        db.add(SiemEvent(
            connector_id=connector_id,
            source_system="LevelProfileManager",
            event_type=norm(sec.event_type, "SECURITY_EVENT"),
            severity=norm(sec.severity, "INFO"),
            status="OPEN" if norm(sec.severity, "INFO") in ["HIGH", "CRITICAL"] else "CLOSED",
            username=sec.username,
            ip_address=sec.ip_address,
            correlation_key=key,
            raw_message=sec.detail,
            normalized_message=sec.detail or sec.event_type,
        ))
        created += 1
    db.commit()
    return {"status": "ok", "created": created, "source": "security_events"}


def siem_dashboard(db: Session) -> dict:
    connectors = db.scalars(select(SiemConnector)).all()
    events = db.scalars(select(SiemEvent).order_by(SiemEvent.id.desc()).limit(1000)).all()
    by_sev = Counter([e.severity for e in events])
    by_type = Counter([e.event_type for e in events])
    by_source = Counter([e.source_system or "UNKNOWN" for e in events])
    open_events = sum(1 for e in events if e.status == "OPEN")
    critical = by_sev.get("CRITICAL", 0)
    high = by_sev.get("HIGH", 0)
    risk_score = min(100, critical * 25 + high * 12 + open_events * 2)
    recs = []
    if critical:
        recs.append("Có sự kiện CRITICAL, cần kích hoạt quy trình ứng cứu sự cố và rà soát hồ sơ liên quan.")
    if high:
        recs.append("Có sự kiện HIGH, cần phân công cán bộ ATTT xử lý trong SLA.")
    if not connectors:
        recs.append("Chưa cấu hình SIEM connector. Nên seed connector mặc định và cấu hình kết nối SOC/SIEM.")
    if not recs:
        recs.append("Không có cảnh báo SIEM nghiêm trọng trong dữ liệu hiện tại.")
    return {
        "total_connectors": len(connectors),
        "enabled_connectors": sum(1 for c in connectors if c.is_enabled),
        "total_events": len(events),
        "open_events": open_events,
        "critical_events": critical,
        "high_events": high,
        "by_severity": dict(by_sev),
        "by_event_type": dict(by_type),
        "top_source_systems": [{"source": k, "count": v} for k, v in by_source.most_common(10)],
        "risk_score": risk_score,
        "recommendations": recs,
    }


def correlation_summary(db: Session) -> dict:
    rules = db.scalars(select(SiemCorrelationRule).where(SiemCorrelationRule.is_enabled == True)).all()  # noqa: E712
    events = db.scalars(select(SiemEvent).where(SiemEvent.status == "OPEN")).all()
    findings = []
    for rule in rules:
        matched = [e for e in events if (not rule.event_type or e.event_type == rule.event_type) and SEVERITY_SCORE.get(e.severity, 0) >= SEVERITY_SCORE.get(rule.min_severity, 0)]
        if len(matched) >= rule.threshold_count:
            findings.append({
                "rule_code": rule.rule_code,
                "rule_name": rule.rule_name,
                "matched_count": len(matched),
                "risk_score": rule.risk_score,
                "action_hint": rule.action_hint,
            })
    return {"enabled_rules": len(rules), "open_events": len(events), "findings": findings, "highest_risk_score": max([f["risk_score"] for f in findings], default=0)}
