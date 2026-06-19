from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_cors_origins, settings
from app.middleware.audit_middleware import AuditMiddleware
from app.middleware.rate_limit_middleware import SimpleRateLimitMiddleware
from app.middleware.request_id_middleware import RequestIdMiddleware
from app.middleware.security_headers_middleware import SecurityHeadersMiddleware

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Ứng dụng quản lý hồ sơ đề xuất cấp độ an toàn hệ thống thông tin",
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(SimpleRateLimitMiddleware)
app.add_middleware(AuditMiddleware)
app.add_middleware(RequestIdMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    return {
        "message": "Level Profile Manager API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
    }
