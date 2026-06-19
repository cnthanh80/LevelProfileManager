from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Ứng dụng quản lý hồ sơ đề xuất cấp độ an toàn hệ thống thông tin",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    return {
        "message": "Level Profile Manager API",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
    }
