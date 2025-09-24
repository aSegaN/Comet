from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import health


app = FastAPI(title="Alarms API", version="0.1.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health.router, prefix="/api")


@app.get("/")
def root():
    return {"service": "alarms-api", "env": settings.environment}