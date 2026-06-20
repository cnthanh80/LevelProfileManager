from fastapi import APIRouter
from app.api.v1.endpoints import assessment_portal, digital_dossier, real_signature, access_control, ai_classification, audit_logs, auth, checklists, compliance, dashboard, document_templates, enterprise_dashboard, executive_dashboard_v2, evidence_documents, exported_documents, health, information_systems, level_profiles, notifications, organizations, risk_register, security_requirements, security_hardening, system, users, workflow, periodic_reviews, release

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(information_systems.router, prefix="/information-systems", tags=["information-systems"])
api_router.include_router(level_profiles.router, prefix="/level-profiles", tags=["level-profiles"])
api_router.include_router(security_requirements.router, prefix="/security-requirements", tags=["security-requirements"])
api_router.include_router(checklists.router, tags=["profile-checklists"])
api_router.include_router(evidence_documents.router, tags=["evidence-documents"])
api_router.include_router(workflow.router, tags=["workflow"])
api_router.include_router(dashboard.router, tags=["dashboard"])
api_router.include_router(enterprise_dashboard.router, tags=["enterprise-dashboard"])

api_router.include_router(exported_documents.router, tags=["exported-documents"])

api_router.include_router(notifications.router, tags=["notifications"])
api_router.include_router(audit_logs.router, tags=["audit-logs"])

api_router.include_router(compliance.router, tags=["compliance-engine"])

api_router.include_router(periodic_reviews.router, tags=["periodic-reviews"])

api_router.include_router(document_templates.router, tags=["document-templates", "government-documents"])

api_router.include_router(access_control.router, tags=["access-control", "ldap-sso-foundation"])

api_router.include_router(system.router, tags=["system", "production-hardening"])

api_router.include_router(security_hardening.router, tags=["security-hardening"])

api_router.include_router(release.router, tags=["release-2.0", "uat-readiness"])

api_router.include_router(digital_dossier.router, tags=["digital-dossier", "digital-signature"])

api_router.include_router(risk_register.router, tags=["risk-register", "sla-management"])

api_router.include_router(assessment_portal.router, tags=["assessment-portal"])

api_router.include_router(executive_dashboard_v2.router, tags=["executive-dashboard", "leadership-dashboard"])

api_router.include_router(ai_classification.router, tags=["ai-classification", "level-recommendation"])

api_router.include_router(real_signature.router, tags=["real-digital-signature", "signature-gateway"])
