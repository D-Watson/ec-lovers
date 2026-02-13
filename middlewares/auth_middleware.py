from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
import util

# 定义不需要认证的路由
PUBLIC_PATHS = ["/metrics", "/user/login", "/user/register", "/user/send_email_code"]


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method == "OPTIONS":
            return await call_next(request)
        # 检查是否为公开路径
        if any(request.url.path.startswith(path) for path in PUBLIC_PATHS):
            return await call_next(request)
        print("All headers:", dict(request.headers))
        # 获取请求头中的认证信息
        user_id = request.headers.get("X-User-Id")
        token = request.headers.get("X-Token")
        print(user_id, token)
        # 验证认证信息
        if not user_id or not token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing authentication headers"}
            )

        if not util.validate_token(user_id, token):
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid credentials"}
            )

        # 将用户信息存储到请求状态中
        request.state.user_id = user_id
        request.state.token = token

        # 继续处理请求
        response = await call_next(request)
        return response
