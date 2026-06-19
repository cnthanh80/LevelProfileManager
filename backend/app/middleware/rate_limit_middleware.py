from __future__ import annotations

import time
from collections import defaultdict, deque
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.config import get_rate_limit_exclude_paths, settings


class SimpleRateLimitMiddleware(BaseHTTPMiddleware):
    """In-memory per-IP rate limiter for a single-container deployment.

    It is disabled by default. For multi-replica production, replace with Redis/API Gateway.
    """

    def __init__(self, app):
        super().__init__(app)
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        excluded = get_rate_limit_exclude_paths()
        if any(request.url.path.startswith(path) for path in excluded):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - 60
        bucket = self._requests[client_ip]

        while bucket and bucket[0] < window_start:
            bucket.popleft()

        if len(bucket) >= settings.RATE_LIMIT_REQUESTS_PER_MINUTE:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded", "limit_per_minute": settings.RATE_LIMIT_REQUESTS_PER_MINUTE},
            )

        bucket.append(now)
        return await call_next(request)
