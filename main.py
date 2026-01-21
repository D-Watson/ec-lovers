from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers import lovers_controller
import uvicorn

app = FastAPI(
    title="My Love App",
    description="情侣互动 API",
    version="1.0.0"
)
app.include_router(lovers_controller.router)
# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或指定具体前端地址，如 ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法（GET, POST, OPTIONS 等）
    allow_headers=["*"],  # 允许所有 headers
)
@app.get("/")
def root():
    return {"message": "Welcome to Love API!"}


if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8080)