from pydantic import BaseModel
import os


class Settings(BaseModel):
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    database_url: str = os.getenv("DATABASE_URL", "postgresql+psycopg://asegan:asega%401965@db:5432/comet")
    environment: str = os.getenv("ENVIRONMENT", "development")
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:3000")


settings = Settings()
