# middleware.py
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from core import REQUEST_COUNT, REQUEST_LATENCY


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response: Response = await call_next(request)
        process_time = time.time() - start_time

        # 获取路径（可选：规范化路径，比如 /items/{id} → /items/:id）
        path = request.url.path
        method = request.method
        status = response.status_code

        # 记录指标
        REQUEST_LATENCY.labels(method=method, path=path).observe(process_time)
        REQUEST_COUNT.labels(method=method, path=path, status=status).inc()

        return response
