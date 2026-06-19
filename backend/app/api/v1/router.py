from fastapi import APIRouter
from app.api.v1.endpoints import audit_logs, auth, checklists, dashboard, evidence_documents, exported_documents, health, information_systems, level_profiles, notifications, organizations, security_requirements, users, workflow

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

api_router.include_router(exported_documents.router, tags=["exported-documents"])

api_router.include_router(notifications.router, tags=["notifications"])
api_router.include_router(audit_logs.router, tags=["audit-logs"])
