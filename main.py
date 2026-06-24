from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.requests import Request

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import controllers
import uvicorn
from middlewares import PrometheusMiddleware, AuthMiddleware
from starlette.responses import Response
from settings import cfg

app = FastAPI(
    title="My Love App",
    description="情侣互动 API",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cfg.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(PrometheusMiddleware)
app.add_middleware(AuthMiddleware)
app.include_router(controllers.router)
app.include_router(controllers.photo)
app.include_router(controllers.user_router)


@app.get("/")
def root():
    return {"message": "Welcome to Love API!"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    print("Incoming request:", request.url)
    return await call_next(request)


if __name__ == '__main__':
    uvicorn.run(app, host=cfg.SERVER_HOST, port=cfg.SERVER_PORT)
