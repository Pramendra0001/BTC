from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from typing import List, Union

class Settings(BaseSettings):
    PROJECT_NAME: str = "BTC-SHIELD Backend"
    API_V1_STR: str = "/api"
    
    DATABASE_URL: str = "sqlite:///btcshield.db"
    
    JWT_SECRET: str = "supersecretkey-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 24 * 8  # 8 days
    
    CORS_ORIGINS: List[str] = ["*"]
    
    AI_PROVIDER: str = "mock"
    LOG_LEVEL: str = "INFO"
    MAX_UPLOAD_SIZE_MB: int = 50
    INGESTION_BATCH_SIZE: int = 1000

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
