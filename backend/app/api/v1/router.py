from fastapi import APIRouter
from app.api.v1.endpoints import auth, health, information_systems, level_profiles, organizations, users

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(information_systems.router, prefix="/information-systems", tags=["information-systems"])
api_router.include_router(level_profiles.router, prefix="/level-profiles", tags=["level-profiles"])
