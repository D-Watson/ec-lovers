from fastapi import FastAPI
from controllers import lovers_controller
import uvicorn

app = FastAPI(
    title="My Love App",
    description="情侣互动 API",
    version="1.0.0"
)
app.include_router(lovers_controller.router)
@app.get("/")
def root():
    return {"message": "Welcome to Love API!"}


if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8080)