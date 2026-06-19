from __future__ import annotations

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.config import settings


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Attach a request id to every request/response for troubleshooting."""

    async def dispatch(self, request: Request, call_next):
        header_name = settings.REQUEST_ID_HEADER
        request_id = request.headers.get(header_name) or str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers[header_name] = request_id
        return response
